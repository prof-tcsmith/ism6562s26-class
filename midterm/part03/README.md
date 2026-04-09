# Midterm Part 3 — Adding Cassandra for Real-Time Order Ingestion

**ISM 6562 - Big Data for Business Applications**

The third part of the midterm. The sales shards from Part 2 can't keep up with the velocity of incoming web/mobile order events. You add a Cassandra cluster to absorb the high-velocity write stream, then extend the ETL job to merge the Cassandra-staged orders into the existing warehouse.

This is your first taste of **polyglot persistence**: PostgreSQL for transactional and analytical workloads where its strengths matter (joins, ACID, ad-hoc SQL), Cassandra for the write-heavy ingestion path where Postgres struggles.

## What's in this folder

```
part03/
├── README.md
├── docker-compose.yaml                # 2 sales shards + HR + warehouse + 3-node Cassandra + ETL
├── ism6562-midterm-part03.html        # full assignment instructions
├── init/
│   ├── sales-shard-ne-init.sql        # NE sales shard
│   ├── sales-shard-se-init.sql        # SE sales shard
│   ├── hr-init.sql                    # HR
│   ├── warehouse-init.sql             # warehouse star-schema
│   ├── cassandra-init.cql             # Cassandra keyspace + tables (query-first design)
│   └── cassandra-seed.sh              # seeds Cassandra with starter data
└── etl/
    ├── Dockerfile
    ├── crontab
    ├── entrypoint.sh
    └── etl_script.py                  # ETL: now reads from both Postgres shards AND Cassandra
```

## Reading the assignment

Open `ism6562-midterm-part03.html`. It explains the polyglot architecture, the query-first Cassandra schema design choices, and what your team needs to deliver.

## Starting the environment

```bash
cd midterm/part03
docker compose up -d
```

The Cassandra nodes take ~60-90 seconds to form a ring before the seed script runs. Watch progress with:

```bash
docker logs -f cassandra-node1
```

## Memory note

This stack runs **2 Postgres shards + HR Postgres + warehouse Postgres + 3 Cassandra nodes + ETL container**. That's about 5-6 GB of RAM. Close other Docker containers from earlier weeks before starting.

## Cleaning up

```bash
docker compose down -v
```

## Submission

Submit your team's Part 3 deliverables to Canvas by the deadline listed there.
