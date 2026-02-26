#!/bin/bash
# Cassandra Seed Script
# Uses Python + cassandra-driver to execute CQL init file (cqlsh not available).

echo "Seeding Cassandra schema and data..."

python3 - <<'PYEOF'
import os
import sys
import time

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

hosts = os.environ.get("CASSANDRA_HOSTS", "cassandra-node1").split(",")

# Wait for Cassandra to be ready
print(f"Waiting for Cassandra at {hosts}...")
cluster = None
for attempt in range(30):
    try:
        cluster = Cluster(hosts)
        session = cluster.connect()
        session.execute("DESCRIBE KEYSPACES")
        print("Cassandra is ready.")
        break
    except Exception as e:
        print(f"  Attempt {attempt+1}: Cassandra not ready ({e}), waiting 5s...")
        if cluster:
            try:
                cluster.shutdown()
            except:
                pass
            cluster = None
        time.sleep(5)
else:
    print("ERROR: Cassandra did not become ready after 150 seconds.", file=sys.stderr)
    sys.exit(1)

# Check if already seeded
try:
    session.set_keyspace("techretail_orders")
    rows = session.execute("SELECT count(*) FROM orders_by_customer")
    count = rows.one()[0]
    if count > 0:
        print(f"Cassandra already seeded ({count} orders found). Skipping.")
        cluster.shutdown()
        sys.exit(0)
except Exception:
    pass  # Keyspace doesn't exist yet, proceed with seeding

# Read and execute CQL file
cql_path = "/app/cassandra-init.cql"
print(f"Loading CQL from {cql_path}...")

with open(cql_path, "r") as f:
    content = f.read()

# Split on semicolons, filter out empty/comment-only statements
statements = []
for stmt in content.split(";"):
    cleaned = stmt.strip()
    # Remove lines that are only comments
    lines = [l for l in cleaned.split("\n") if l.strip() and not l.strip().startswith("--")]
    if lines:
        statements.append(cleaned + ";")

executed = 0
for stmt in statements:
    # Skip pure comment blocks
    non_comment = [l for l in stmt.split("\n") if l.strip() and not l.strip().startswith("--")]
    if not non_comment:
        continue
    try:
        session.execute(SimpleStatement(stmt))
        executed += 1
    except Exception as e:
        # Print but continue (some may be IF NOT EXISTS)
        print(f"  Warning executing statement: {e}")

print(f"Cassandra seed complete. Executed {executed} statements.")
cluster.shutdown()
PYEOF
