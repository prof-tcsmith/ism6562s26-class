# Midterm Part 2 — Sharding the Sales Database

**ISM 6562 - Big Data for Business Applications**

The second part of the midterm. The sales database from Part 1 has outgrown a single instance. You shard it horizontally across two regional shards (Northeast and Southeast) and update the ETL pipeline to query both shards and merge the results.

## What's in this folder

```
part02/
├── README.md
├── docker-compose.yaml                # 2 sales shards + HR + warehouse + ETL
├── ism6562-midterm-part02.html        # full assignment instructions
├── init/
│   ├── sales-shard-ne-init.sql        # Northeast sales shard schema + seed data
│   ├── sales-shard-se-init.sql        # Southeast sales shard schema + seed data
│   ├── hr-init.sql                    # HR DB (unchanged from Part 1)
│   └── warehouse-init.sql             # warehouse star-schema (unchanged from Part 1)
└── etl/
    ├── Dockerfile
    ├── crontab
    ├── entrypoint.sh
    └── etl_script.py                  # updated ETL: queries both shards
```

## Reading the assignment

Open `ism6562-midterm-part02.html` in a browser. It explains the sharding strategy, the cross-shard query challenges, and what your team needs to deliver.

## Starting the environment

```bash
cd midterm/part02
docker compose up -d
```

## What's different from Part 1

- The sales database is now **two** Postgres instances instead of one (`sales_ne`, `sales_se`).
- The ETL job (`etl/etl_script.py`) connects to both shards, queries each, and merges the results before loading the warehouse.
- HR and warehouse databases stay the same — they were never the bottleneck.

## Connecting

| Service | Port | Database |
|---|---|---|
| Sales shard NE | `localhost:5511` | `sales_ne` |
| Sales shard SE | `localhost:5512` | `sales_se` |
| HR | `localhost:5502` | `hrdb` |
| Warehouse | `localhost:5503` | `warehouse` |

(Exact ports may differ — check `docker-compose.yaml` for the canonical mapping.)

## Cleaning up

```bash
docker compose down -v
```

## Submission

Submit your team's Part 2 deliverables to Canvas by the deadline listed there.
