# Final Project: PrecisionParts Manufacturing — Supply Chain & Quality Analytics

## Company Background

PrecisionParts is a Tier 1 automotive components manufacturer with eight factories spread across four states. The company produces brake assemblies, transmission housings, and engine mounts for six major automakers. Their supply chain is vast: 200 suppliers provide raw materials and sub-components, and 50 distribution centers handle logistics to customer assembly plants. PrecisionParts employs 12,000 workers across three shifts and operates over 800 CNC machines, stamping presses, and robotic assembly cells. The company generated $2.4B in revenue last year, but margins have been squeezed by rising defect rates and inventory inefficiencies that the COO describes as "death by a thousand cuts."

The quality crisis emerged gradually over the past 18 months. Defect rates across all product lines have increased by 15%, from 1.2% to 1.38%, which may sound small but translates to roughly 45,000 additional defective parts per quarter. Each defective brake assembly that reaches a customer's assembly line triggers a $2,500 containment charge, and three OEM customers have issued formal quality warnings. Root cause analysis has been nearly impossible because quality inspection data, production line sensor data, and supplier performance records live in separate systems maintained by different teams. The VP of Quality suspects that a handful of suppliers with declining material quality are responsible for most of the increase, but she cannot prove it without joining data that has never been joined before.

Simultaneously, the CFO has flagged inventory carrying costs of $30M annually --- roughly 25% higher than industry benchmarks. Warehouses are overstocked on slow-moving parts and frequently short on high-demand components, leading to both waste and expedited shipping charges. The company's ERP system generates purchase orders based on fixed reorder points that were last calibrated two years ago, with no consideration of actual demand trends, supplier lead time variability, or seasonal patterns. PrecisionParts has committed to building a data-driven manufacturing intelligence platform that integrates production, quality, supply chain, and equipment data into a single analytical pipeline. The goal is to reduce defects by 40%, cut inventory carrying costs by $8M, and implement real-time machine monitoring to prevent unplanned downtime that currently costs $50K per hour.

## The Business Problem

PrecisionParts faces several quantifiable operational challenges:

- **Rising defect rates**: Defects have increased 15% year-over-year, costing approximately $28M annually in scrap, rework, and customer containment charges. The root causes are unknown because quality data is disconnected from production and supplier data.

- **Inventory imbalance**: $30M in annual carrying costs, with 35% of SKUs overstocked by more than 60 days of supply while 12% of SKUs experience stockouts at least once per quarter. Each stockout triggers $15K--$50K in expedited freight costs.

- **Supplier quality opacity**: The company tracks on-time delivery but has no systematic way to correlate supplier material quality with downstream defect rates. Supplier quality scores are updated manually on a quarterly basis, months after problems begin.

- **Unplanned downtime**: Equipment failures cause an average of 180 hours of unplanned downtime per factory per year, at a cost of approximately $50K per hour. Maintenance is calendar-based rather than condition-based, meaning machines are either serviced too frequently (wasting capacity) or not frequently enough (causing failures).

- **Shift-level variation**: Anecdotal evidence suggests that defect rates vary significantly across shifts and operators, but this has never been quantified because production and quality data are in different systems.

## Available Data Sources

The following datasets are available in the project data repository:

| Source File | Format | Records | Description |
|---|---|---|---|
| `production-lines.csv` | CSV | 800,000 | Production run records: line, factory, product, batch, cycle time, units produced, defects, operator, shift, machine temperature, and vibration readings |
| `quality-inspections.json` | JSON | 100,000 | Inspection results with defect type, severity, and dimensional measurements including tolerance and deviation |
| `inventory-levels.csv` | CSV | 200,000 | Daily warehouse inventory snapshots: on-hand quantity, reserved quantity, reorder point, lead time, cost, and supplier |
| `supplier-performance.json` | JSON | 50,000 | Delivery records with expected vs actual dates, quantity accuracy, quality scores, and supplier country of origin |
| `equipment-sensors.csv` | CSV | 500,000 | Machine telemetry: temperature, vibration, power consumption, oil pressure, and operational status at regular intervals |

## Business Questions

PrecisionParts' leadership team needs answers to these questions:

1. **Defect prediction**: Can production line sensor data (machine temperature, vibration levels) predict defect likelihood before parts are produced? What sensor thresholds are associated with elevated defect rates?

2. **Supplier-defect linkage**: Which suppliers' materials correlate with higher downstream defect rates? Is supplier quality score a reliable predictor of incoming material quality, or are there lagging indicators the current system misses?

3. **Inventory optimization**: Based on historical consumption patterns and supplier lead time variability, what should reorder points be for each SKU to achieve a 98% service level while minimizing carrying costs?

4. **Shift and operator analysis**: Are there statistically significant differences in defect rates across shifts (day/evening/night) and operators? If so, what interventions (training, staffing changes) would have the highest impact?

5. **Predictive maintenance**: Can equipment sensor trends (rising temperature, increasing vibration, declining oil pressure) predict impending machine failures? What is the optimal maintenance trigger threshold that minimizes both unplanned downtime and unnecessary maintenance?

6. **Real-time anomaly detection**: Can the system detect abnormal machine behavior in near real-time and alert operators before a quality excursion or equipment failure occurs?

## Stage Guide

The following describes the **minimum floor** for each stage. Strong submissions will go well beyond these starting points.

### Stage 1: Data Lake Foundation (HDFS)

- Load all five data files into HDFS, preserving original formats
- Design HDFS zones: `raw/` for landing, `processed/` for cleaned data, `analytics/` for final outputs
- The production-lines and equipment-sensors files are largest and should span multiple HDFS blocks
- Consider partitioning by factory_id in processed zones to enable efficient per-factory analysis

### Stage 2: Batch Transformation (Spark)

- **Clean**: Validate sensor readings against physical limits (e.g., temperature > 0, vibration >= 0); standardize timestamps; handle nulls in quality inspection measurements
- **Join**: Link production-lines with quality-inspections on batch_id to connect manufacturing conditions with inspection outcomes. Join inventory-levels with supplier-performance on supplier_id to correlate supply chain factors with stock levels.
- **Aggregate**: Compute defect rates by factory, shift, and operator. Compute supplier scorecards (on-time %, quality %, quantity accuracy). Calculate inventory turnover and days-of-supply metrics per SKU. Compute machine health baselines (mean and standard deviation of sensor readings per machine).
- Write analytical datasets to HDFS in Parquet format

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- Equipment sensor data is the natural streaming source --- in production, sensors emit readings every 5 seconds per machine
- Design a Kafka topic for machine telemetry events (machine_id, factory_id, timestamp, temperature, vibration, power_consumption, oil_pressure)
- Use Spark Structured Streaming to compute rolling averages and detect when current readings deviate significantly from baseline
- Trigger alerts when vibration exceeds the machine's historical 95th percentile or when temperature rises more than 2 standard deviations above the running average

### Stage 4: Pipeline Orchestration (Airflow)

- Build a DAG that ingests daily production and quality data, runs Spark transformations, updates supplier scorecards and defect analytics, and exports summary reports
- Include quality gates: verify record counts match expected daily volumes, check that all referenced batch_ids in inspections exist in production data, validate sensor reading ranges
- Consider separate DAG branches for supply chain analytics vs production quality analytics, merging at a final reporting task
- The streaming pipeline for equipment monitoring runs continuously alongside the batch DAG

## Evaluation Focus

A strong PrecisionParts submission will demonstrate:

- **Cross-domain joins** that connect the full chain: supplier materials to production conditions to quality outcomes --- this is where the most valuable insights live
- **Quantified defect analysis** that goes beyond counts to identify root causes (which supplier + which machine + which shift = highest defect rate)
- **Practical anomaly detection** in the streaming component --- thresholds should be data-driven (based on historical baselines), not arbitrary
- **Inventory analytics** that translate into actionable recommendations (adjusted reorder points, supplier diversification)
- **A well-designed Airflow DAG** with meaningful quality gates that would catch real data issues in a production environment

## Data Access

Download the datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/08-supplychain-manufacturing
```

Each team member should clone or download the data and place it in their project's `data/` directory before beginning pipeline development.
