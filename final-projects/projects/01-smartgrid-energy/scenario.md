# Final Project: VoltEdge Power — Smart Grid Analytics

## Company Background

VoltEdge Power is a regional electric utility serving 2.5 million residential, commercial, and industrial customers across four southeastern states. Founded in 1962 as a small municipal power cooperative, VoltEdge grew through a series of acquisitions in the 1990s and 2000s, inheriting a patchwork of grid infrastructure that spans multiple generations of technology. Some substations still run on equipment installed in the 1970s, while newer sections of the network feature smart meters and digital sensors — creating a hybrid grid that is difficult to monitor holistically.

The company operates 14 grid zones, each served by a network of transformers, substations, and distribution lines. In 2024, VoltEdge completed a $120M smart meter rollout, installing digital meters on every residential and commercial account. They also deployed 8,000 grid sensors on transformers and distribution lines to provide real-time voltage, current, and frequency readings. Despite this investment in instrumentation, VoltEdge's analytics infrastructure remains primitive — most data sits in flat files and siloed databases, and outage response is still largely reactive.

VoltEdge's CEO has mandated a "predictive grid" initiative, recognizing that the data to prevent outages already exists — it just isn't being used. The company has hired your team as data engineering consultants to build the analytics foundation that will power this initiative. Your job is to unify the disparate data sources into a coherent data lake, build the transformation pipelines to generate actionable insights, and design a real-time monitoring system that can detect grid anomalies before they cause outages.

## The Business Problem

VoltEdge experienced **12,000 outages** in the past year, affecting an average of 85 customers per event. The direct cost in emergency repairs, crew overtime, and equipment replacement was **$112M**. Indirect costs — including customer compensation, regulatory fines for prolonged outages, and reputational damage — added another **$68M**, bringing the total annual cost of outages to approximately **$180M**.

The root causes break down as follows:

- **Weather-related** (35%): Storms, ice, high winds, and lightning strikes
- **Equipment failure** (28%): Aging transformers and distribution lines failing under load
- **Overload** (22%): Grid zones exceeding capacity during peak demand, especially summer afternoons
- **Animal interference** (8%): Squirrels, birds, and other wildlife causing short circuits
- **Unknown** (7%): Causes not identified in post-incident investigation

The most frustrating category for VoltEdge leadership is equipment failure. Post-mortem analysis consistently shows that warning signs — voltage fluctuations, rising transformer temperatures, abnormal current readings — were present in the sensor data hours or even days before the failure. But without automated monitoring, nobody was watching. Meanwhile, the preventive maintenance program operates on fixed schedules rather than condition-based triggers, meaning technicians sometimes service healthy equipment while deteriorating equipment goes unattended.

VoltEdge estimates that a predictive analytics system could prevent **30–40% of equipment-related outages** and reduce overload events by **50%** through better demand forecasting — potentially saving **$50–70M annually**.

## Available Data Sources

| Source | Format | Records | Key Fields |
|--------|--------|---------|------------|
| Power Consumption | CSV | 1,300,000 | meter_id, timestamp, kwh_reading, customer_type, grid_zone, temperature_f |
| Grid Sensors | JSON | 400,000 | sensor_id, timestamp, voltage, current_amps, frequency_hz, grid_zone, transformer_id, status |
| Outage History | CSV | 50,000 | outage_id, start_time, end_time, grid_zone, cause, customers_affected, duration_minutes |
| Weather Stations | JSON | 100,000 | station_id, timestamp, temp_f, humidity, wind_speed_mph, precipitation_in, condition, grid_zone |
| Maintenance Logs | CSV | 30,000 | work_order_id, transformer_id, date, type, cost, technician_id, resolution_time_hours |

### Data Notes

- **Power Consumption**: Readings are at 15-minute intervals from smart meters. Customer types include residential, commercial, and industrial. The `temperature_f` field comes from the nearest weather station at the time of the reading.
- **Grid Sensors**: Each sensor is mounted on a transformer and reports voltage, current, and frequency. The nested JSON structure groups readings under a `readings` key. Status values are `normal`, `warning`, and `critical` — but these are based on simple threshold rules that VoltEdge admits are poorly calibrated.
- **Outage History**: Covers the past 3 years. Duration ranges from a few minutes to several days for major storm events.
- **Weather Stations**: VoltEdge maintains 14 weather stations (one per grid zone). Readings are hourly.
- **Maintenance Logs**: Includes preventive (scheduled), corrective (responding to a known issue), and emergency (responding to an outage) work orders.

## Business Questions

The VoltEdge executive team needs your analysis to address the following questions:

1. **Outage Prediction**: Can we predict which grid zones are at highest risk of outage in the next 24–48 hours based on sensor readings, weather forecasts, and historical patterns?
2. **Chronic Overload Zones**: Which grid zones are chronically operating near or above capacity? What times of day and weather conditions trigger overload events?
3. **Maintenance Optimization**: Which transformers should be prioritized for preventive maintenance based on sensor health indicators, age (inferred from maintenance history), and outage history?
4. **Weather Vulnerability**: How does weather affect grid stability across different zones? Are some zones more weather-vulnerable than others, and why?
5. **Customer Impact Analysis**: Which customer types (residential, commercial, industrial) bear the greatest burden of outages? What is the estimated cost per customer-hour of outage by type?
6. **Sensor Anomaly Patterns**: What voltage and current patterns precede equipment failures? Can we define better thresholds for the sensor warning/critical status levels?
7. **Maintenance ROI**: Is preventive maintenance actually reducing outages? Compare outage rates and durations for transformers with regular preventive maintenance vs. those maintained only reactively.

## Stage Guide

This section provides **minimum scaffolding** for each stage — think of these as the floor, not the ceiling. Strong projects will go well beyond these suggestions.

### Stage 1: Data Lake Foundation (HDFS)

- **Zone design**: Create landing, curated, and analytics zones in HDFS
- **Landing zone**: Load all five raw data sources in their original formats (CSV and JSON)
- **Format strategy**: Consider converting JSON sensor data to Parquet in the curated zone for query performance. CSV files with simple schemas may also benefit from Parquet conversion.
- **Partitioning hints**: Power consumption data could be partitioned by `grid_zone` or by date. Outage history might partition well by `cause` or `year`.
- **Replication**: Higher replication for outage history (critical for regulatory reporting) vs. standard replication for high-volume sensor data

### Stage 2: Batch Transformation (Spark)

- **Key joins**: Enrich grid sensor readings with weather data (join on grid_zone + timestamp window). Join outage history with maintenance logs on transformer_id to see if maintained transformers have fewer outages.
- **Aggregations**: Daily/weekly power consumption summaries by grid zone. Average sensor readings by transformer (to establish baselines). Outage frequency and duration by zone, cause, and season.
- **Derived features**: Calculate "days since last maintenance" for each transformer. Compute rolling average voltage deviation per sensor. Flag consumption readings that exceed the zone's 95th percentile.
- **Output**: Write curated datasets as Parquet partitioned by grid_zone and date to the curated zone. Write aggregated analytics tables to the analytics zone.

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- **Streaming source**: Grid sensors are the natural streaming data source — they emit readings every 10 seconds in production.
- **Kafka topic design**: Consider a `grid-sensor-readings` topic keyed by `sensor_id` or `grid_zone`.
- **Real-time logic**: Detect voltage anomalies (below 110V or above 130V). Implement a sliding window (e.g., 5-minute) to track average voltage per zone and alert when it deviates from the historical baseline by more than 2 standard deviations.
- **Alert events**: Produce alerts to a separate `grid-alerts` topic when anomalies are detected.
- **Architecture decision**: Consider whether a Lambda architecture (batch reprocessing + real-time) or Kappa architecture (stream-only) is more appropriate for this use case. VoltEdge needs both historical analysis and real-time monitoring — what does that suggest?

### Stage 4: Pipeline Orchestration (Airflow)

- **Batch DAG**: Schedule the Spark batch pipeline to run daily. Tasks might include: ingest new data to landing zone, run Spark transforms, write to curated zone, run quality checks, write to analytics zone.
- **Quality gates**: Validate that sensor readings fall within physically plausible ranges (e.g., voltage between 0 and 500V). Check for data completeness — flag days where a grid zone has fewer than expected readings. Validate that the number of output records is within expected bounds.
- **Monitoring DAG**: Create a separate DAG that checks streaming pipeline health — is the Kafka consumer group lagging? Are alerts being generated at an expected rate (not zero, not suspiciously high)?
- **Retry and SLA**: Set SLAs for the batch pipeline (must complete within 2 hours). Add retry logic for Spark tasks that may fail due to cluster resource contention.

## Evaluation Focus

Strong submissions for this project will demonstrate:

- **Predictive insight**: Moving beyond descriptive statistics to actually identify patterns that precede outages — even a simple model or heuristic that flags high-risk zones is valuable
- **Cross-source enrichment**: The real power of this dataset comes from joining sensor, weather, maintenance, and outage data together. Projects that keep these sources siloed will miss the most interesting findings.
- **Practical alerting**: A streaming pipeline that generates meaningful, actionable alerts — not just "voltage is low" but "voltage on transformer T-4521 in Zone 7 has been declining for 3 hours during a heat wave, and this transformer has not been maintained in 18 months"
- **Business framing**: Connecting technical findings back to VoltEdge's bottom line — quantify the potential savings, prioritize recommendations by impact

## Data Access

Download the project datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/01-smartgrid-energy
```

All data files are gzip-compressed (`.csv.gz` and `.json.gz`). Decompress them after downloading with `gunzip *.gz` or load them directly in Spark (which reads gzipped files natively). Clone the data repo and copy files into your project's `data/` directory, or reference them directly from HDFS after loading.
