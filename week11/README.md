# Week 11 — Pipeline Orchestration & the Modern Data Stack

**ISM 6562 - Big Data for Business Applications**

## Topics

- The Orchestration layer of the modern data stack (on top of Storage/Transform/Stream from Weeks 8–10)
- Apache Airflow: DAGs, operators, task dependencies, retries, backfill
- Idempotency, quality gates, SLAs, and alerting
- Data quality checks as explicit pipeline stages (fail-fast, observable)
- Where this sits vs. industry tools: Snowflake, dbt, Fivetran, Databricks Workflows
- Two complete orchestrated pipelines: HealthPulse (daily) and GreenRoute (weekly)

## What's in this folder

```
week11/
├── README.md                                         # this file
├── docker-compose.yml                                # Airflow + Postgres + Spark
├── docker/
│   ├── Dockerfile.airflow                            # custom Airflow image with Spark submit deps
│   └── Dockerfile.spark                              # uid-aligned Spark image (shared with Week 9/10)
├── dags/
│   ├── healthpulse_daily_pipeline.py                 # diamond-pattern DAG with quality gate
│   ├── healthpulse_late_arrivals.py                  # FileSensor DAG that waits for a file to land
│   └── greenroute_weekly_report.py                   # linear weekly DAG with XCom reporting
├── ism6562-week11-assignment.html                    # graded assignment
├── notebooks/
│   └── ism6562-week11-companion-notebook.ipynb       # in-class walkthrough of the Airflow UI
└── data/
    ├── healthpulse/
    │   ├── daily-patient-feed/                       # three daily CSV drops (2026-04-28..30)
    │   └── quality-test-bad-data.csv                 # intentionally malformed rows
    └── greenroute/
        ├── weekly-gps-summary/                       # two weeks of pre-aggregated GPS data
        └── quality-test-bad-gps.json                 # intentionally bad GPS payloads
```

## Setting up the stack

The lab runs Airflow 2.8 on Postgres (LocalExecutor) alongside a 1-worker Spark
cluster, so DAGs can call `spark-submit` for real distributed jobs.

```bash
cd week11
docker compose up -d
```

Wait ~60 seconds for the one-shot `airflow-init` container to create the
metadata schema and admin user, then for the webserver health check to pass.

- **Airflow Web UI**: <http://localhost:8080>  (admin / admin)
- **Spark Master Web UI**: <http://localhost:8081>
- **Spark Worker Web UI**: <http://localhost:8082>
- **Postgres (for Airflow metadata)**: <localhost:5432> (user `airflow`, password `airflow`)

To stop and clean up: `docker compose down` (add `-v` to delete the named
volumes used for Postgres data and Airflow logs).

## The three provided DAGs

All three DAGs are mounted from `./dags/` into the scheduler and webserver
containers, so any edit you make on your host refreshes in Airflow within
~30 seconds (the default scheduler parse interval).

Each DAG demonstrates a different operator family so you can see the full
palette: BashOperator + PythonOperator (healthpulse_daily_pipeline and
greenroute_weekly_report) and the FileSensor (healthpulse_late_arrivals).

### `healthpulse_daily_pipeline`

Schedule: `0 2 * * *` (daily at 02:00 UTC). Five tasks arranged in a
diamond:

```
  ingest_patient_feed
         │
    validate_data          ← quality gate; fails if error_rate > 5%
       /    \
  transform   quality_report
       \    /
    load_to_warehouse
         │
    send_notification
```

The `validate_data` PythonOperator pushes `total_records`, `error_count`,
and `error_rate` to XCom; `quality_report` pulls them downstream. Retries
are configured (2 attempts, 5 min delay), and a 30-minute execution
timeout prevents runaway tasks.

### `healthpulse_late_arrivals`

Schedule: `0 6 * * *` (daily at 06:00 UTC, when the arrival window opens).
Four tasks in a linear chain, introduced by a **FileSensor** that polls
every 60 seconds for the day's patient-feed file (up to a 2-hour timeout)
before any downstream work runs:

```
wait_for_daily_feed  (FileSensor)
         │
    validate_file
         │
  process_late_arrival
         │
   notify_on_call
```

The sensor uses `mode="reschedule"` to free its worker slot between
pokes — important when many sensors are waiting on slow-arriving files.

### `greenroute_weekly_report`

Schedule: `0 2 * * MON` (Mondays at 02:00 UTC). Four tasks in a linear
chain: validate GPS data → aggregate fleet metrics → generate report →
send notification.

## Running the companion notebook

1. Start the stack (`docker compose up -d`) and wait for all services healthy.
2. Open <http://localhost:8080> and sign in as `admin` / `admin`.
3. You'll see both DAGs on the home page. Toggle each to "unpaused".
4. Open the companion notebook
   (`notebooks/ism6562-week11-companion-notebook.ipynb`) in your local
   Jupyter / VS Code — it walks through the Airflow UI (Grid view, Graph
   view, task logs, XCom) and sends `docker exec` commands to trigger and
   inspect DAG runs.

## The graded assignment

Open `ism6562-week11-assignment.html` in your browser. The assignment asks
you to:

1. Stand up the stack and explore the Airflow Web UI.
2. **Create a personalized DAG** (`pipeline_{LAST4}`) that ingests,
   validates, and loads a small dataset, using XCom to pass metrics between
   tasks.
3. **Data quality engineering** — write a Python callable that fails the
   DAG when error-rate thresholds are exceeded, and prove the failure
   propagates downstream.
4. **Trigger and monitor** — trigger runs manually, investigate a failing
   task in the UI, and show the Grid view with at least one successful run.
5. **Backfill** — run a backfill for a past date and capture the result.
6. **Architecture memo (400–600 words)** — map the stack you built this
   semester onto a cloud-native alternative (Snowflake + dbt + Airflow, or
   Databricks Workflows).

Submit a single PDF to Canvas by the deadline.

## Memory requirements

The full stack (Postgres + Airflow webserver + scheduler + Spark master +
1 worker) uses about **5 GB of RAM** while a DAG is running. If your
laptop is tight on memory, stop the Week 9 or Week 10 stacks before
starting this one.

## Troubleshooting

- **"Invalid login credentials"**: the admin user is `admin` / `admin`
  (created by the one-shot `airflow-init` container). If the user was
  never created, run `docker compose logs airflow-init` — you should see
  "User admin created".
- **DAGs don't appear in the UI**: the scheduler parses DAGs every 30
  seconds. If you just edited a file in `./dags/`, wait a minute. Check
  `docker compose logs airflow-scheduler | grep -i error` for parse errors.
- **"No module named airflow"**: you tried to run a DAG file locally on
  your host. DAG files only need to run inside the Airflow container —
  the scheduler imports them, not you.
- **Backfill hangs in "queued"**: Airflow won't execute DAG runs whose
  execution date is in the future. Use a past date
  (e.g. `--exec-date 2026-04-17T02:00:00+00:00`).

## Getting help

- Lecture slides and recorded discussion are on Canvas.
- For technical questions, post in the Week 11 Canvas discussion or attend
  the extra-help session on Saturday.
