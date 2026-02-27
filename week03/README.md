# Week 03: PostgreSQL Performance and Indexing

This folder contains two Docker Compose files — one for the in-class demo and one for the assignment. Both use the same IoT sensor database (`sensordb`) but run in separate containers with separate data volumes, so they do not interfere with each other.

## Files

| File | Purpose |
|------|---------|
| `docker-compose.demo.yaml` | In-class demonstration environment |
| `docker-compose.assignment.yaml` | Assignment environment for indexing exercises |
| `init/sensor-init.sql` | Database initialization script (shared by both) |

## Running a Specific Docker Compose File

Because there is no default `docker-compose.yaml`, you must use the `-f` flag to specify which file to run.

### Demo Environment (in-class)

```bash
# Start
docker compose -f docker-compose.demo.yaml up -d

# Check status
docker compose -f docker-compose.demo.yaml ps

# Connect to the database
docker compose -f docker-compose.demo.yaml exec postgres psql -U student -d sensordb

# View logs
docker compose -f docker-compose.demo.yaml logs

# Stop and remove containers (keeps data)
docker compose -f docker-compose.demo.yaml down

# Stop and remove containers AND data volumes (fresh start)
docker compose -f docker-compose.demo.yaml down -v
```

### Assignment Environment

```bash
# Start
docker compose -f docker-compose.assignment.yaml up -d

# Check status
docker compose -f docker-compose.assignment.yaml ps

# Connect to the database
docker compose -f docker-compose.assignment.yaml exec postgres psql -U student -d sensordb

# View logs
docker compose -f docker-compose.assignment.yaml logs

# Stop and remove containers (keeps data)
docker compose -f docker-compose.assignment.yaml down

# Stop and remove containers AND data volumes (fresh start)
docker compose -f docker-compose.assignment.yaml down -v
```

## Important Notes

- Both environments use the **same ports** (PostgreSQL: 5501, pgAdmin: 8200). You must stop one environment before starting the other.
- Use `down -v` to delete the data volume and get a clean database. Use `down` (without `-v`) to keep your data for next time.
- pgAdmin is available at [http://localhost:8200](http://localhost:8200) with credentials `student@student.com` / `student`.

## Access

| Service | URL / Port | Credentials |
|---------|-----------|-------------|
| PostgreSQL | `localhost:5501` | `student` / `student` |
| pgAdmin | [http://localhost:8200](http://localhost:8200) | `student@student.com` / `student` |
