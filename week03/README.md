# Week 03: PostgreSQL Performance and Indexing

This folder contains two separate environments for Week 03, each in its own subfolder. Both use the same IoT sensor database (`sensordb`) but run in separate containers with separate data volumes, so they do not interfere with each other.

## Folder Structure

```
week03/
├── lab/           ← In-class lab (follow along with slides)
│   ├── docker-compose.yaml
│   ├── ism6562-week03-lab.html
│   └── init/sensor-init.sql
└── assignment/    ← Take-home assignment (indexing exercises)
    ├── docker-compose.yaml
    ├── ism6562-week03-assignment.html
    └── init/sensor-init.sql
```

## Lab Environment (in-class)

```bash
cd lab
docker compose up -d
docker compose exec postgres psql -U student -d sensordb

# When finished
docker compose down -v
```

## Assignment Environment

```bash
cd assignment
docker compose up -d
docker compose exec postgres psql -U student -d sensordb

# When finished
docker compose down -v
```

## Important Notes

- Both environments use the **same ports** (PostgreSQL: 5501, pgAdmin: 8200). You must stop one environment before starting the other.
- Use `down -v` to delete the data volume and get a clean database. Use `down` (without `-v`) to keep your data for next time.

## Access

| Service | URL / Port | Credentials |
|---------|-----------|-------------|
| PostgreSQL | `localhost:5501` | `student` / `student` |
| pgAdmin | [http://localhost:8200](http://localhost:8200) | `student@student.com` / `student` |
