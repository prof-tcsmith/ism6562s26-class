# Final Project: AgriFlow — Precision Agriculture Analytics

## Company Background

AgriFlow is an agricultural technology company that manages data infrastructure for 50 large-scale farms spanning 200,000 acres across the Midwest. The farms primarily grow three commodity crops — corn, soybeans, and wheat — and collectively represent over $400M in annual revenue. AgriFlow was founded in 2020 by a group of agricultural engineers and data scientists who saw an opportunity to bring modern analytics to an industry that still relies heavily on intuition, almanac-style rules of thumb, and fixed schedules for critical decisions like irrigation, fertilization, and harvest timing.

Over the past three years, AgriFlow invested $8M deploying IoT soil sensors across its member farms. Each farm has sensors placed on a grid pattern, with one sensor per 10 acres, measuring soil moisture, temperature, pH, and nutrient levels (nitrogen, phosphorus, and potassium — the "NPK" trio that drives plant growth). These sensors transmit readings every 30 minutes via cellular networks to AgriFlow's central data store. Combined with satellite weather data, equipment telemetry, and historical yield records, AgriFlow sits on a rich dataset that could revolutionize how its member farms operate.

The problem is that AgriFlow built the data collection infrastructure before building the analytics infrastructure. The sensor data arrives reliably but sits in JSON files that nobody analyzes systematically. Weather data comes from a separate provider and lives in its own CSV format. Yield records are maintained in spreadsheets by individual farm managers. Equipment usage logs come from the manufacturers' telematics systems. None of these data sources have been integrated, and AgriFlow's agronomists are making recommendations based on small subsets of data rather than the full picture. Your team has been engaged to build the data platform that turns AgriFlow's data investment into actionable intelligence.

## The Business Problem

AgriFlow's member farms face three critical challenges that data analytics could address:

**Yield Optimization**: Average crop yields across AgriFlow's farms vary by as much as **40% between the best and worst performing fields**, even within the same farm growing the same crop. AgriFlow's agronomists believe that much of this variation is driven by suboptimal irrigation and fertilization — but without systematic analysis of the relationship between soil conditions, weather, inputs, and yields, they cannot pinpoint what to change. A **10% improvement in average yield** across the portfolio would generate an additional **$40M in annual revenue** for the member farms.

**Water Management**: Irrigation is the largest controllable cost for these farms, accounting for **$25M annually** across the portfolio. Currently, irrigation schedules are set at the beginning of each season based on historical averages and adjusted manually by farm managers based on visual inspection and gut feel. AgriFlow estimates that **30% of irrigation water is wasted** — applied when soil moisture is already adequate or applied uniformly when only certain sections of a field need water. In a region facing increasing water scarcity and rising water costs, optimizing irrigation is both an economic and environmental imperative.

**Frost and Weather Risk**: Unexpected frost events cost AgriFlow's farms an average of **$12M per year** in crop damage. The farms subscribe to regional weather forecasts, but these operate at county-level granularity and miss microclimate variations — a frost event might hit the low-lying fields of one farm while sparing a neighboring farm on higher ground. AgriFlow's soil temperature sensors could provide field-level frost prediction with much higher accuracy, but this capability has never been built.

Additionally, market timing — knowing when to sell harvested crops based on price trends and futures markets — represents a significant revenue opportunity. Farms that time their sales well can earn **15–20% more** than those that sell at harvest.

## Available Data Sources

| Source | Format | Records | Key Fields |
|--------|--------|---------|------------|
| Soil Sensors | JSON | 500,000 | sensor_id, farm_id, field_id, timestamp, soil_moisture_pct, soil_temp_f, ph_level, nitrogen_ppm, phosphorus_ppm, potassium_ppm |
| Crop Yields | CSV | 100,000 | farm_id, field_id, year, crop_type, acres, yield_bushels_per_acre, fertilizer_applied_lbs, irrigation_gallons, planting_date, harvest_date |
| Weather Daily | CSV | 150,000 | station_id, farm_id, date, high_temp_f, low_temp_f, precipitation_in, humidity_pct, solar_radiation_wm2, wind_mph, frost_risk |
| Equipment Usage | JSON | 80,000 | equipment_id, farm_id, timestamp, type, hours_operated, fuel_gallons, field_id, operator_id |
| Market Prices | CSV | 20,000 | date, crop_type, price_per_bushel, futures_price, region |

### Data Notes

- **Soil Sensors**: Readings every 30 minutes from IoT sensors. The JSON structure nests the NPK readings under a `nutrients` key and moisture/temperature under a `conditions` key. Sensor coverage varies by farm — newer farms have denser grids.
- **Crop Yields**: Historical records going back 8 years. Each record represents one field's yield for one growing season. Fertilizer and irrigation totals are for the entire season. Planting and harvest dates indicate the growing window.
- **Weather Daily**: From NOAA-based weather stations, one per farm or shared among nearby farms. The `frost_risk` boolean indicates whether the low temperature approached freezing (below 35°F). Solar radiation is relevant for photosynthesis modeling.
- **Equipment Usage**: Telematics data from tractors, harvesters, irrigators, and sprayers. The `hours_operated` and `fuel_gallons` fields help estimate operating costs. Equipment assigned to specific fields enables correlation with yield data.
- **Market Prices**: Daily commodity prices for corn, soybeans, and wheat, including spot prices and futures prices. Regional variations reflect local supply/demand dynamics.

## Business Questions

AgriFlow's leadership and member farm managers need your analysis to address the following:

1. **Yield Prediction**: What combination of soil conditions (moisture, pH, nutrients), weather patterns, and farming inputs (fertilizer, irrigation) best predicts crop yield? Can we identify the "recipe" for high-yielding fields?
2. **Irrigation Optimization**: Based on soil moisture sensor data and weather forecasts, when should each field be irrigated and how much water should be applied? Which fields are currently being over-irrigated or under-irrigated?
3. **Soil Health Trends**: Are any fields showing declining soil health over time (dropping pH, nutrient depletion, moisture retention loss)? Which farms are maintaining or improving soil quality, and what practices differentiate them?
4. **Frost Alert System**: Can we build a field-level frost prediction system using soil temperature sensors and weather data that provides earlier and more accurate warnings than county-level forecasts?
5. **Equipment Efficiency**: Which farms are using equipment most efficiently (lowest fuel per acre, shortest harvest windows)? Are there operational practices that correlate with higher yields?
6. **Market Timing**: Based on historical price patterns and seasonal trends, when is the optimal time to sell each crop type? How much revenue could farms gain by shifting their sales timing?
7. **Field Comparison**: What distinguishes the top-performing fields from the bottom-performing fields? Control for crop type, weather, and soil type to isolate the impact of management decisions.

## Stage Guide

This section provides **minimum scaffolding** for each stage — think of these as the floor, not the ceiling. Strong projects will go well beyond these suggestions.

### Stage 1: Data Lake Foundation (HDFS)

- **Zone design**: Create landing, curated, and analytics zones in HDFS
- **Landing zone**: Load all five data sources in their original formats (JSON and CSV)
- **Format considerations**: Soil sensor JSON is the largest dataset and should be converted to Parquet in the curated zone. Flatten the nested nutrient and condition readings during conversion.
- **Partitioning hints**: Soil sensors could be partitioned by `farm_id` or by date. Crop yields partition naturally by `year` and `crop_type`. Weather data could partition by `farm_id`.
- **Replication**: Standard replication for most sources. Consider higher replication for crop yield data (irreplaceable historical records).

### Stage 2: Batch Transformation (Spark)

- **Key joins**: Join soil sensor readings with weather data (on farm_id + date) to correlate soil conditions with weather events. Join crop yields with seasonal averages of soil readings and weather to build yield prediction features. Merge equipment usage with field-level yield data to assess equipment efficiency.
- **Aggregations**: Seasonal soil condition averages and trends by field. Growing degree days accumulated between planting and harvest dates. Total equipment hours and fuel per acre per field.
- **Derived features**: Calculate "days of adequate moisture" during growing season. Compute NPK ratios and compare to recommended ranges by crop type. Build a soil health index combining moisture retention, pH stability, and nutrient levels over time.
- **Output**: Write curated datasets as Parquet partitioned by farm and year. Build analytics-ready tables for yield prediction and irrigation optimization.

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- **Streaming source**: Soil sensors are the natural streaming source — reporting every 30 minutes in production. Weather alerts could also stream.
- **Kafka topic design**: Consider a `soil-readings` topic keyed by `farm_id` and a `farm-alerts` topic for detected conditions.
- **Real-time logic**: Detect drought risk when soil moisture drops below 20%. Detect frost risk when soil temperature approaches 32°F and trending downward. Use a sliding window (e.g., 2-hour) to track moisture and temperature trends per field.
- **Alert events**: Generate alerts with farm_id, field_id, alert_type (drought/frost), current reading, trend direction, and recommended action.
- **Architecture decision**: Consider whether agricultural monitoring benefits from Lambda architecture (historical yield analysis + real-time field monitoring) or if a Kappa architecture is sufficient.

### Stage 4: Pipeline Orchestration (Airflow)

- **Batch DAG**: Schedule daily processing aligned with the sensor reporting cadence. Tasks: ingest new sensor and weather data, run Spark transforms, update soil health scores, run quality checks, refresh analytics tables.
- **Quality gates**: Validate sensor readings are within physically plausible ranges (e.g., soil moisture 0–100%, pH 3.0–10.0). Check for sensor outages (missing readings for >2 hours). Verify cross-source consistency (e.g., if weather shows heavy rain, soil moisture should increase).
- **Monitoring DAG**: Monitor sensor data freshness — alert if a farm's sensors stop reporting. Check streaming pipeline health.
- **Retry and SLA**: Set SLAs for daily batch completion. Build a seasonal "harvest readiness" report DAG that runs weekly during harvest season.

## Evaluation Focus

Strong submissions for this project will demonstrate:

- **Agricultural domain understanding**: Show that you understand the farming context — growing seasons, the relationship between soil health and yield, the economics of irrigation. You don't need to be an agronomist, but your analysis should make agronomic sense.
- **Temporal analysis**: Agriculture is fundamentally seasonal. The best insights will come from analyzing data across growing seasons, tracking trends over years, and understanding how timing (of planting, irrigation, harvest) affects outcomes.
- **Sensor data engineering**: IoT sensor data is noisy, has gaps, and requires careful handling. Projects that address data quality issues (outlier detection, gap filling, sensor calibration drift) will stand out.
- **Actionable field-level recommendations**: "Field 12 on Farm 7 should reduce irrigation by 15% based on consistently high soil moisture readings and below-average yields despite adequate water" is far more useful than "some fields are over-irrigated."

## Data Access

Download the project datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/03-agriflow-farming
```

All data files are gzip-compressed (`.csv.gz` and `.json.gz`). Decompress them after downloading with `gunzip *.gz` or load them directly in Spark (which reads gzipped files natively). Clone the data repo and copy files into your project's `data/` directory, or reference them directly from HDFS after loading.
