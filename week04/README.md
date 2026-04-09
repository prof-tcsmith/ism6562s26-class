# Week 04 — Scaling, Sharding & Distributed SQL

**ISM 6562 - Big Data for Business Applications**

## Topics

- Vertical vs horizontal scaling strategies for relational databases
- Table partitioning (extending Week 3) for managing large tables on a single instance
- Manual sharding: distributing data across multiple Postgres instances
- Cross-shard challenges (joins, aggregations, transactions)
- A first look at distributed SQL solutions (Citus, CockroachDB) — students survey one in the midterm Part 4

## What's in this folder

```
week04/
├── README.md
├── partitioning-lab/         # In-class lab on table partitioning
│   ├── docker-compose.yaml
│   ├── ism6562-week04-partitioning-lab.ipynb        # full notebook
│   ├── ism6562-week04-partitioning-lab-short.ipynb  # condensed version
│   └── init/sensor-init.sql                          # IoT sensor schema
├── sharding-lab/             # In-class lab on manual sharding
│   ├── docker-compose.yaml
│   ├── ism6562-week04-sharding-lab.ipynb            # full notebook
│   └── ism6562-week04-sharding-lab-short.ipynb     # condensed version
└── assignment/               # Take-home assignment
    ├── docker-compose.yaml
    └── init/ecommerce-init.sql                      # ecommerce schema
```

Each subdirectory has its own Docker environment so they don't interfere with each other.

## Running each environment

```bash
# Partitioning lab
cd week04/partitioning-lab
docker compose up -d
# Open the .ipynb in JupyterLab or VS Code and run cells in order
docker compose down -v        # when done

# Sharding lab
cd week04/sharding-lab
docker compose up -d
# Open the .ipynb and follow along
docker compose down -v        # when done

# Assignment
cd week04/assignment
docker compose up -d
# See the assignment instructions on Canvas
docker compose down -v        # when done
```

## Notebook variants — full vs short

The `-short.ipynb` versions are condensed (~30% fewer cells) for in-class pacing. The full notebooks include extra exposition, exercises, and bonus material — use those when you work through the lab on your own.

## Important notes

- Each environment uses its own Postgres ports — see the individual `docker-compose.yaml` files for specifics.
- Always run `down -v` between environments to delete the data volume and avoid port/volume conflicts.
- The sharding lab spins up multiple Postgres instances; make sure your machine has enough RAM (~3-4 GB free).

## Getting help

- Lecture slides and the in-class walkthrough are on Canvas.
- For questions, post in the Week 4 Canvas discussion or attend the Saturday extra-help session.
