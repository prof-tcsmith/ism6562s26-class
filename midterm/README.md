# Midterm Group Project — ISM 6562

Four-part midterm covering operational databases, data warehousing, ETL pipelines, sharding, polyglot persistence with Cassandra, and distributed SQL database evaluation.

## Team Formation

This is a **group project**. Teams must have **4 to 5 students**.

**Deadline:** Submit your team to the professor and the GA by **February 28th**. Any students not part of a group after the deadline will be randomly assigned to a team.

**Important constraints:**

- Due to Canvas splitting undergraduate and graduate sections, **teams must consist of students at the same level** — all undergraduates or all graduates. Mixed teams are not permitted.
- We cannot help you form teams. If you want to work with a friend, you need to enlist 2--3 others to get a full team.

**To submit your team**, send an email to the professor and the GA:

- **Subject:** ISM 6562 — [Your Team Name]
- **Body:** A list of all team member full names (4 to 5 students)

## Structure

```
midterm-project/
├── part01/   Operational DBs, Star Schema, and ETL
├── part02/   Sharding the Sales Database
├── part03/   Adding Cassandra for Real-Time Order Ingestion
└── part04/   Distributed SQL Database Presentations
```

Parts 1–3 are hands-on Docker assignments — run `docker compose down -v` between parts. Part 4 is a research presentation (no Docker).

## Part 1: Operational Databases, Data Warehousing, and ETL

Five-service Docker environment: sales-db, hr-db, warehouse-db (star schema), etl-service (Python+cron), and pgAdmin. Students explore OLTP vs OLAP, star schemas, and ETL idempotency.

```bash
cd part01
docker compose up -d
```

## Part 2: Sharding the Sales Database

Six-service environment replacing the single sales-db with two regional shards (Southeast and Northeast). Students diagnose a broken ETL, fix it to extract from both shards, and analyze cross-shard query challenges.

```bash
cd part02
docker compose up -d
```

## Part 3: Adding Cassandra for Real-Time Order Ingestion

Eight-service environment adding a two-node Cassandra cluster for high-velocity order writes. Students explore query-first design, denormalization trade-offs, and modify the ETL to extract orders from Cassandra. Teaches polyglot persistence.

```bash
cd part03
docker compose up -d   # Cassandra takes 60-90s to initialize
```

## Part 4: Distributed SQL Database Presentations

Team presentation assignment — no Docker infrastructure. Each team selects a distributed SQL database (Citus, CockroachDB, YugabyteDB, TiDB, FoundationDB, Fauna, Spanner, Vitess, or SingleStore), researches it against standardized evaluation criteria, and delivers a 7–10 minute presentation with Q&A.

## Credentials

All PostgreSQL databases: `student` / `student`
pgAdmin: `student@student.com` / `student`

## Ports

| Service | Part 1 | Part 2 | Part 3 |
|---|---|---|---|
| sales-db | 5501 | — | — |
| sales-shard-se | — | 5511 | 5511 |
| sales-shard-ne | — | 5512 | 5512 |
| hr-db | 5502 | 5502 | 5502 |
| warehouse-db | 5503 | 5503 | 5503 |
| pgAdmin | 8200 | 8200 | 8200 |
| Cassandra node 1 | — | — | 9042 |
| Cassandra node 2 | — | — | 9043 |
