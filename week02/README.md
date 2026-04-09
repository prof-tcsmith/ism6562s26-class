# Week 02 — Docker, Terminal, and Git Introduction

**ISM 6562 - Big Data for Business Applications**

## Topics

- Linux command-line and terminal basics
- Version control with Git and GitHub
- Docker architecture: images, containers, volumes, networks
- Docker Compose for multi-container applications
- Hands-on: PostgreSQL + pgAdmin via `docker-compose`

## What's in this folder

```
week02/
├── README.md              # this file
└── docker-compose.yaml    # Postgres + pgAdmin stack for the in-class walkthrough
```

The lab content for Week 2 is delivered live in class as a guided walkthrough — there is no separate notebook or written lab document. This `docker-compose.yaml` is the environment we spin up together to practice container lifecycle, volumes, and networking against a real Postgres + pgAdmin setup.

## Starting the environment

```bash
cd week02
docker compose up -d
```

When you're done:

```bash
docker compose down       # keep your data volume for next session
docker compose down -v    # delete the volume and start clean next time
```

## Access

| Service | URL / Port | Credentials |
|---|---|---|
| PostgreSQL | `localhost:5432` | (defined in `docker-compose.yaml`) |
| pgAdmin | <http://localhost:8123> | (defined in `docker-compose.yaml`) |

## Getting help

- Lecture slides and the in-class walkthrough are on Canvas.
- For questions, post in the Week 2 Canvas discussion or attend the Saturday extra-help session.
