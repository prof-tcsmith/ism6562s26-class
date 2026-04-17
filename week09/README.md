# Week 9 — Spark & Distributed Transformation

**ISM 6562 - Big Data for Business Applications**

## Topics

- The Transform layer of the ELT pipeline (Week 8 covered the Storage layer)
- Apache Spark architecture: driver, cluster manager, workers, executors, tasks
- The Spark DataFrame API: transformations (lazy) vs actions (trigger execution)
- Spark SQL and the Catalyst optimizer
- Joining, aggregating, windowing, and repartitioning across a distributed cluster
- Writing curated outputs in Parquet (columnar, schema-embedded, compressed)
- Reading Avro telemetry written by Week 8
- Two business scenarios continued from Week 8: HealthPulse and GreenRoute

## What's in this folder

```
week09/
├── README.md                                       # this file
├── docker-compose.yml                              # Spark cluster + Jupyter
├── docker/
│   └── Dockerfile.spark                            # custom Spark image (uid-aligned jovyan user)
├── ism6562-week09-assignment.html                  # graded assignment
├── notebooks/
│   └── ism6562-week09-companion-notebook.ipynb     # in-class walkthrough (opens in Jupyter)
└── data/                                           # new Week 9 lab data
    ├── healthpulse/
    │   ├── patient-records/hospital_04_patients.csv
    │   └── lab-results/lab_results.json
    └── greenroute/
        ├── route-plans/route_plans.json
        └── fuel-logs/fuel_logs.csv
```

The companion notebook also downloads Week 8 HealthPulse and GreenRoute files
(including the 168 Avro GPS-telemetry partitions from Week 8's data lake), so
you do not need to have Week 8 running — just the Week 9 cluster below.

## Setting up the Spark cluster

The lab runs on a standalone Spark 3.5 cluster with two workers and an
in-cluster Jupyter server for interactive PySpark.

```bash
cd week09
docker compose up -d
```

On first run, Docker builds a small custom Spark image (`ism6562/spark-jovyan:3.5.0`)
so the driver and workers share the same `jovyan` uid — this prevents
"Mkdirs failed: Permission denied" errors when the driver writes partitioned
output. The build takes under 10 seconds.

Wait ~30 seconds for the Spark Master health check to pass, then:

- **Jupyter (PySpark)**: <http://localhost:8888?token=spark>
- **Spark Master Web UI**: <http://localhost:8080>
- **Spark Worker 1 UI**: <http://localhost:8081>
- **Spark Worker 2 UI**: <http://localhost:8082>
- **Spark Application UI**: <http://localhost:4040> (active only while a job is running)

To stop and clean up the cluster: `docker compose down` (add `-v` to also
delete the named volumes used for worker scratch space and Jupyter home).

## Running the companion notebook

The companion notebook runs **inside the Jupyter container**, so you do not
need a local Python environment:

1. Start the cluster (`docker compose up -d`) and wait for all services to be healthy.
2. Open <http://localhost:8888?token=spark> in your browser.
3. In the Jupyter file browser, open `notebooks/ism6562-week09-companion-notebook.ipynb`.
4. Run cells in order — the first code cell creates a SparkSession pointing at
   `spark://spark-master:7077`, the second cell downloads all lab data into
   `/home/jovyan/data/`, and the rest walk through the two business scenarios.

The `notebooks/` directory on your host is bind-mounted into the Jupyter
container, so any new notebooks you create or edits you make persist outside
the container.

## The graded assignment

Open `ism6562-week09-assignment.html` in your browser. The assignment asks you to:

1. Bring up the Spark cluster and verify worker registration, cores, and memory.
2. **HealthPulse schema harmonization** — load four hospital CSVs with
   divergent schemas, standardize column names and types, and produce a
   unified patient DataFrame.
3. **HealthPulse claims enrichment** — join patients to insurance claims and
   lab results, compute cost-per-visit and care-gap metrics.
4. **GreenRoute GPS analytics** — read the Avro GPS telemetry from Week 8,
   compute per-driver distance and idle time, join against fuel logs.
5. Write curated outputs as Parquet under `/home/jovyan/data/output-{LAST4}/`,
   where `{LAST4}` is the last four digits of your USF student ID.
6. Capture screenshots of the Spark Master UI showing your running application
   and the job DAG.

Submit a single PDF to Canvas by the deadline.

## Memory requirements

The full stack (Spark master + 2 workers + Jupyter) uses about **6 GB of RAM**
when a job is running. If your laptop is tight on memory, close earlier
Docker stacks (Hadoop from Week 8, Cassandra/Postgres from earlier weeks)
before starting this one:

```bash
docker ps
docker stop <container-name>
```

## Troubleshooting

- **Jupyter won't open**: double-check you used the token in the URL
  (`?token=spark`). Without the token, Jupyter rejects the connection.
- **"Connection refused" from driver to master**: make sure all three Spark
  services are in the `Up (healthy)` state — `docker compose ps`. The master
  health check can take up to 30 seconds after `compose up`.
- **"Mkdirs failed: Permission denied" when writing output**: confirm you did
  not override the image to `apache/spark:3.5.0` directly — the custom
  `ism6562/spark-jovyan:3.5.0` image is required so the driver and workers
  run at the same uid.
- **Port conflicts** (`port is already allocated`): Week 9 uses 8888, 8080,
  8081, 8082, 7077, and 4040. If one is taken, stop the offending container
  before bringing Week 9 up.

## Getting help

- Lecture slides and recorded discussion are on Canvas.
- For technical questions about the lab, post in the Week 9 Canvas
  discussion or attend the extra-help session on Saturday.
