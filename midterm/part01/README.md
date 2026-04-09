# Midterm Part 1 — Operational DBs, Star Schema, and ETL

**ISM 6562 - Big Data for Business Applications**

The first part of the four-part midterm group project. You stand up three operational PostgreSQL instances (sales, HR, warehouse), then build a Python ETL job that joins data from all three and loads it into a star-schema data warehouse.

## What's in this folder

```
part01/
├── README.md
├── docker-compose.yaml                # 3 Postgres instances + ETL container
├── ism6562-midterm-part01.html        # full assignment instructions
├── init/                              # database initialization scripts
│   ├── sales-init.sql                 # sales operational DB schema + seed data
│   ├── hr-init.sql                    # HR operational DB schema + seed data
│   └── warehouse-init.sql             # star-schema warehouse (empty fact + dimension tables)
└── etl/                               # ETL container build context
    ├── Dockerfile
    ├── crontab                        # scheduled ETL run
    ├── entrypoint.sh
    └── etl_script.py                  # Python ETL job
```

## Reading the assignment

Open `ism6562-midterm-part01.html` in a browser. It walks through the architecture, the deliverables, and the grading rubric.

## Starting the environment

```bash
cd midterm/part01
docker compose up -d
```

The three Postgres containers come up first; the ETL container waits for them to become healthy before starting its scheduled run.

## Connecting to the databases

| Service | Port | Database | Credentials |
|---|---|---|---|
| Sales operational | `localhost:5501` | `salesdb` | (see `init/sales-init.sql`) |
| HR operational | `localhost:5502` | `hrdb` | (see `init/hr-init.sql`) |
| Warehouse | `localhost:5503` | `warehouse` | (see `init/warehouse-init.sql`) |
| pgAdmin | <http://localhost:8200> | — | (defined in `docker-compose.yaml`) |

You can connect with `psql` directly:

```bash
psql -h localhost -p 5501 -U <user> -d salesdb
```

Or use pgAdmin in the browser.

## Cleaning up

```bash
docker compose down       # keep data volumes
docker compose down -v    # wipe everything and start fresh
```

## Submission

Submit your team's deliverables for Part 1 to Canvas by the deadline listed there. See the assignment HTML for what counts as "complete" for this part.
