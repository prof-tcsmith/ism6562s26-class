# ISM 6562 - Big Data for Business Applications (Spring 2026)

Course materials for ISM 6562, University of South Florida.

## Getting Started

Clone this repository to your local machine:

```bash
git clone https://github.com/prof-tcsmith/ism6562s26-class.git
```

If you already cloned it, pull the latest changes:

```bash
cd ism6562s26-class
git pull
```

## Prerequisites

- **Docker Desktop** installed and running ([download](https://www.docker.com/products/docker-desktop/))
- **Git** installed ([download](https://git-scm.com/downloads))
- A terminal application (Terminal on macOS/Linux, Git Bash or WSL on Windows)

## Repository Structure

```
ism6562s26-class/
├── week02/
│   └── docker-compose.yaml
├── week03/
│   ├── docker-compose.yaml
│   └── init/
├── midterm/
│   ├── part01/   (Operational DBs, Star Schema, ETL)
│   ├── part02/   (Sharding the Sales Database)
│   └── part03/   (Cassandra for Order Ingestion)
└── ...
```

Navigate to the appropriate folder and follow the instructions provided in the Canvas assignment.

## Midterm Project

The midterm has three independent parts. Run `docker compose down -v` between parts.

```bash
cd ism6562s26-class/midterm/part01
docker compose up -d
```

See the assignment documents on Canvas for detailed instructions.
