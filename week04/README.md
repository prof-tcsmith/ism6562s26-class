# Week 04: Partitioning & Sharding Labs

Two hands-on labs exploring how to scale PostgreSQL — first on a single server (partitioning), then across multiple servers (sharding).

## Lab 1: Table Partitioning

Optimize a 500K-row IoT sensor database using range, list, and hash partitioning on a single PostgreSQL instance.

```bash
cd partitioning-lab
docker compose up -d
# Open ism6562-week04-partitioning-lab.ipynb in Jupyter
```

**Ports:** PostgreSQL `5502` | pgAdmin `8201`

## Lab 2: Manual Sharding

Build a 3-shard PostgreSQL cluster for TechMart's regional warehouses. Experience cross-shard query complexity, FK limitations, and coordinator-based aggregation.

```bash
cd sharding-lab
docker compose up -d
# Open ism6562-week04-sharding-lab.ipynb in Jupyter
```

**Ports:** Coordinator `5436` | Shards `5433-5435` | pgAdmin `6050`

## Cleanup

```bash
cd partitioning-lab && docker compose down -v
cd ../sharding-lab && docker compose down -v
```
