# Week 8 — HDFS & the Data Lake

**ISM 6562 - Big Data for Business Applications**

## Topics

- The shift from the bundled-database paradigm to a layered big-data pipeline
- Hadoop ecosystem overview (HDFS, YARN, ecosystem tools)
- HDFS architecture: NameNode (with HA), DataNodes, blocks, replication, rack-aware placement
- The data lake: landing → curated → analytics zones, schema-on-read
- File formats: CSV, JSON, **Avro**, Parquet — when to use each
- Two business scenarios: HealthPulse (healthcare) and GreenRoute (logistics)

## What's in this folder

```
week08/
├── README.md                                       # this file
├── docker-compose.yml                              # 3-DataNode Hadoop cluster
├── ism6562-week08-assignment.html                  # graded assignment
├── ism6562-week08-companion-notebook.ipynb         # in-class walkthrough
└── data/                                           # pre-generated lab data
    ├── healthpulse/
    │   ├── patient-records/
    │   │   ├── hospital_01_patients.csv            # ~878 KB
    │   │   ├── hospital_02_patients.csv            # ~878 KB
    │   │   └── hospital_03_patients.csv            # ~1.07 MB
    │   ├── device-readings/
    │   │   └── device_readings.json                # ~8.9 MB, 50K records
    │   └── insurance-claims/
    │       └── insurance_claims.csv                # ~1.5 MB, 20K claims
    └── greenroute/
        ├── gps-telemetry/
        │   ├── gps_reading.avsc                    # Avro schema
        │   └── day_{01..07}/hour_{00..23}/gps_data.avro    # 168 partition files
        ├── delivery-receipts/
        │   └── delivery_receipts.json
        └── weather/
            └── weather_data.json
```

## Setting up the Hadoop cluster

The lab runs on a 3-DataNode HDFS cluster in Docker.

```bash
cd week08
docker compose up -d
```

Wait ~60 seconds for the NameNode health check to pass, then:

- **NameNode Web UI**: <http://localhost:9870>
- **YARN ResourceManager**: <http://localhost:8088>
- Exec into the NameNode container: `docker exec -it hadoop-namenode bash`

To stop and clean up the cluster: `docker compose down`

## Running the companion notebook

The companion notebook walks through the HealthPulse and GreenRoute scenarios live in class. To run it yourself:

1. Make sure the cluster is up (`docker compose ps` should show all services healthy)
2. Open `ism6562-week08-companion-notebook.ipynb` in JupyterLab or VS Code
3. Run cells in order — the notebook downloads data files from this same `week08/data/` directory in the class repo and uploads them into HDFS

Note that **GPS telemetry is in Avro format** (binary). You cannot `cat` or pretty-print these files at the shell — Spark reads them natively in Week 9. The schema lives in `data/greenroute/gps-telemetry/gps_reading.avsc` if you want to inspect it.

## The graded assignment

Open `ism6562-week08-assignment.html` in your browser. The assignment walks you through:

1. Starting the cluster and capturing a `dfsadmin -report`
2. Designing a personalized 3-zone HDFS directory structure for HealthPulse (every student uses their last 4 USF ID digits in paths)
3. Loading three hospital files plus device readings and insurance claims, then comparing the schema differences across hospitals
4. Replication experiments: increasing RF on PHI data, decreasing on bulk telemetry, computing storage overhead
5. A capacity inventory and two NameNode UI screenshots
6. A 400-600 word memo to HealthPulse's CTO with architecture recommendations

Submit a single PDF to Canvas by the deadline.

## Memory requirements

The full Hadoop cluster uses about 4-6 GB of RAM. If your laptop is tight on memory, close other Docker containers (Postgres, Cassandra from earlier weeks) before starting this one.

## Getting help

- Lecture slides and recorded discussion are on Canvas.
- For technical questions about the lab, post in the Week 8 Canvas discussion or attend the extra-help session on Saturday.
- If `docker compose up` hangs or services don't become healthy, check that ports 9870, 8088, 9000, 9864, 8042 are free on your machine.
