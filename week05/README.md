# Week 05 — CAP Theorem, NoSQL, and Cassandra

**ISM 6562 - Big Data for Business Applications**

## Topics

- The CAP theorem and its implications for distributed databases
- NoSQL database categories and when to use each (key-value, document, column-family, graph)
- Apache Cassandra: wide-column store, ring topology, eventual consistency
- Query-first schema design (the opposite of normalization)
- Hands-on: spinning up a 3-node Cassandra cluster and modeling a query-first schema

## What's in this folder

```
week05/
├── README.md
└── docker-compose.yaml    # 3-node Cassandra cluster
```

The lab content for Week 5 is delivered live in class. The `docker-compose.yaml` here spins up a real 3-node Cassandra ring so you can practice CQL, observe replication factors and consistency levels, and design query-first schemas during the in-class walkthrough.

## Starting the cluster

```bash
cd week05
docker compose up -d
```

Wait ~60-90 seconds for all three nodes to join the ring. You can watch them come up with:

```bash
docker logs -f cassandra-node1
```

When all three nodes report "Startup complete," connect with `cqlsh`:

```bash
docker exec -it cassandra-node1 cqlsh
```

Inside `cqlsh`, verify the ring is healthy:

```cql
DESCRIBE CLUSTER;
SELECT cluster_name, listen_address, rpc_address FROM system.local;
```

When you're done:

```bash
docker compose down       # keep data volumes
docker compose down -v    # wipe data and start fresh next time
```

## Access

| Service | Port | Notes |
|---|---|---|
| Cassandra node 1 (CQL) | `localhost:9042` | Primary client port |
| Cassandra node 2 (CQL) | `localhost:9043` | Same protocol, different host port |
| Cassandra node 3 (CQL) | `localhost:9044` | Same protocol, different host port |

## Memory note

Cassandra is memory-hungry — three nodes together typically need ~3 GB of RAM. Close other heavy Docker containers (Postgres from earlier weeks) before starting this cluster.

## Getting help

- Lecture slides and the in-class walkthrough are on Canvas.
- For questions, post in the Week 5 Canvas discussion or attend the Saturday extra-help session.
