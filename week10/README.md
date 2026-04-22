# Week 10 — Streaming Data & Real-Time Pipelines

**ISM 6562 - Big Data for Business Applications**

## Topics

- The Stream layer of the ELT pipeline (Weeks 8 and 9 covered Storage and Transform)
- Apache Kafka: topics, partitions, consumer groups, retention, offsets
- Event-driven architecture and the publish-subscribe pattern
- Spark Structured Streaming: unbounded tables, `readStream`, `writeStream`, windowed aggregations, watermarks
- Lambda vs Kappa architectures — when and why to choose each
- Two business scenarios continued from Weeks 8–9: HealthPulse (Lambda) and GreenRoute (Kappa)

## What's in this folder

```
week10/
├── README.md                                       # this file
├── docker-compose.yml                              # Kafka + Zookeeper + Spark + Jupyter + Kafka UI
├── docker/
│   └── Dockerfile.spark                            # custom Spark image (uid-aligned jovyan user)
├── ism6562-week10-assignment.html                  # graded assignment
├── notebooks/
│   └── ism6562-week10-companion-notebook.ipynb     # in-class walkthrough (opens in Jupyter)
└── data/                                           # sample events for the two scenarios
    ├── healthpulse/
    │   ├── sample-device-events.json
    │   └── sample-claim-events.json
    └── greenroute/
        ├── sample-gps-events.json
        ├── sample-delivery-events.json
        └── sample-weather-alerts.json
```

Events for the live streaming exercises are generated inside the companion
notebook (and by students in their assignment code); the JSON files in
`data/` are small samples for demos and debugging.

## Setting up the streaming cluster

The lab runs on Kafka 7.5 + Spark 3.5 + Jupyter, with the Provectus
Kafka UI for browser-based topic and message inspection.

```bash
cd week10
docker compose up -d
```

On first run, Docker builds a small custom Spark image
(`ism6562/spark-jovyan:3.5.0`) so the driver and workers share the same
`jovyan` uid. Build takes under 10 seconds.

Wait ~60 seconds for all six services to reach healthy, then:

- **Jupyter (PySpark)**: <http://localhost:8888?token=spark>
- **Spark Master Web UI**: <http://localhost:8080>
- **Spark Worker Web UI**: <http://localhost:8081>
- **Spark Application UI**: <http://localhost:4040> (active only while a streaming job runs)
- **Kafka UI**: <http://localhost:8088> — no login required; use this throughout the lab to inspect topics, partitions, messages, and consumer-group lag

To stop and clean up: `docker compose down` (add `-v` to also delete the
named volumes holding Kafka logs, Zookeeper state, and Spark scratch).

## Running the companion notebook

The notebook runs **inside the Jupyter container**, so you do not need a
local Python environment:

1. Start the cluster (`docker compose up -d`) and wait for all services healthy.
2. Open <http://localhost:8888?token=spark> in your browser.
3. In the Jupyter file browser, open `notebooks/ism6562-week10-companion-notebook.ipynb`.
4. Run cells in order — the first cells create a SparkSession with the
   Kafka connector package, verify Kafka connectivity, create topics,
   and then walk through the two business scenarios.

Keep Kafka UI open in a second browser tab while you run the notebook.
You will see topics appear, partition counts populate, and consumer-group
offsets advance in real time as the notebook produces and consumes events.

## The graded assignment

Open `ism6562-week10-assignment.html` in your browser. The assignment asks you to:

1. Stand up the streaming cluster and create personalized Kafka topics
   (`device-events-{LAST4}`, `gps-stream-{LAST4}`, `claim-events-{LAST4}`).
2. **HealthPulse device pipeline** — produce 100 simulated bedside-device
   events to Kafka, consume them with a Spark Structured Streaming query,
   apply anomaly detection rules, and write the anomaly count per hospital.
3. **GreenRoute GPS pipeline** — apply a windowed aggregation over the
   GPS stream to detect idle trucks (speed < 5 mph for 10+ minutes).
4. **Architecture memo (400–600 words)** — analyze whether HealthPulse
   and GreenRoute should use Lambda or Kappa, defending your choice.
5. Capture two screenshots: the Spark Master UI showing your streaming
   application, and the Kafka UI Topics page showing your three
   personalized topics with partition counts.

Submit a single PDF to Canvas by the deadline.

## Memory requirements

The full stack (Zookeeper + Kafka + Spark master + worker + Jupyter +
Kafka UI) is tuned to stay under **7 GB of RAM** total via explicit
`mem_limit` settings on every service. If your laptop is tight on
memory, close earlier Docker stacks (Hadoop from Week 8, Spark from
Week 9) before starting this one:

```bash
docker ps
docker stop <container-name>
```

## Troubleshooting

- **Jupyter won't open**: double-check you used the token in the URL
  (`?token=spark`). Without the token, Jupyter rejects the connection.
- **Kafka UI shows no cluster**: confirm Zookeeper and Kafka are both
  `Up (healthy)` in `docker compose ps`. Kafka UI depends on Kafka; if
  Kafka is still warming up, refresh in 30 seconds.
- **"Connection refused" when writing to Kafka**: the bootstrap server
  is `kafka:9092` from inside Docker (or `localhost:29092` from your
  host). If you are producing from Python running on your laptop rather
  than in the Jupyter container, use the external listener port 29092.
- **Port conflicts** (`port is already allocated`): Week 10 uses 8888,
  8080, 8081, 8088, 7077, 4040, 9092, 29092, and 2181. If one is
  taken, stop the offending container before bringing Week 10 up.
- **Kafka heap OOM**: Kafka's JVM is capped at 512 MB by
  `KAFKA_HEAP_OPTS`. If a topic has very many partitions or very large
  messages you can raise this in the compose file.

## Getting help

- Lecture slides and recorded discussion are on Canvas.
- For technical questions about the lab, post in the Week 10 Canvas
  discussion or attend the extra-help session on Saturday.
