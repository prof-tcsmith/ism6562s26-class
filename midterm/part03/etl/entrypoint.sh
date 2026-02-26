#!/bin/bash

echo "=== ETL Service Starting ==="

# Pass environment variables to cron
printenv | grep -E '^(SALES_|HR_|WAREHOUSE_|CASSANDRA_)' >> /etc/environment

# Seed Cassandra with schema and data
echo "Seeding Cassandra..."
chmod +x /app/cassandra-seed.sh
/app/cassandra-seed.sh

# Run ETL immediately on startup (may fail if script needs updating)
echo ""
echo "Running initial ETL load..."
python /app/etl_script.py || echo "WARNING: Initial ETL run failed. Check the script and try again."

echo ""
echo "Starting cron for scheduled runs (every 5 minutes)..."

# Start cron in the foreground
cron -f
