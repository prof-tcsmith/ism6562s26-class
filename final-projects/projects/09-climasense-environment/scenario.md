# Final Project: ClimaSense Environment — Urban Air Quality Monitoring

## Company Background

ClimaSense is an environmental technology company that operates a network of 500 air quality monitoring stations deployed across 15 major metropolitan areas. Founded in 2018 by a team of atmospheric scientists and IoT engineers, ClimaSense sells real-time air quality data and predictive analytics to three categories of clients: municipal governments that use the data for public health advisories and urban planning, healthcare networks that correlate pollution levels with emergency department surges, and corporate sustainability teams that need hyperlocal emissions data for ESG reporting. The company's monitoring stations measure six key pollutants --- PM2.5, PM10, ground-level ozone, nitrogen dioxide, sulfur dioxide, and carbon monoxide --- and compute the EPA's Air Quality Index (AQI) at 15-minute intervals.

ClimaSense's value proposition is granularity: while the EPA operates roughly 4,000 monitoring stations across the entire United States, ClimaSense provides 500 stations in just 15 cities, giving clients block-by-block resolution rather than city-wide averages. This matters because air quality can vary dramatically within a single city --- a monitoring station near a highway interchange may read PM2.5 levels three times higher than a station in a nearby park, and residents deserve to know the air quality at their location, not a city-wide average. The company has grown to $35M in annual recurring revenue and recently closed a Series B funding round, but their data infrastructure is buckling under the weight of their ambitions.

The core technical problem is latency and integration. Each monitoring station reports pollutant readings every 15 minutes, generating over 48,000 readings per day across the network. Currently, this data is processed in nightly batch jobs, meaning that the "real-time" air quality maps on ClimaSense's public dashboard are actually 12--24 hours stale. Cities are demanding hourly updates and, critically, real-time alerts when pollution spikes above health thresholds. Beyond the sensor data itself, ClimaSense has identified that integrating weather conditions, traffic patterns, emission source registries, and hospital health incident data dramatically improves their AQI prediction models. But these data sources exist in different formats, different update frequencies, and different systems. Building a unified data pipeline that supports both batch analytics (historical trend analysis, health outcome correlations) and real-time alerting (pollution spike detection, forecast updates) is the company's top engineering priority for the year.

## The Business Problem

ClimaSense faces several pressing challenges:

- **Stale public data**: The dashboard that 2 million monthly visitors rely on shows air quality data that is 12--24 hours old. During a recent wildfire smoke event, the dashboard showed "Good" air quality while residents could literally see the haze. Three city contracts are at risk over this gap.

- **Missed health alerts**: Cities require alerts within 30 minutes when AQI exceeds 150 (unhealthy for all populations). The current batch pipeline cannot meet this SLA. Last quarter, ClimaSense failed to alert on 14 pollution spikes, two of which coincided with elevated emergency room visits for respiratory distress.

- **Predictive gap**: ClimaSense's clients want 6-hour AQI forecasts so cities can issue proactive advisories (e.g., "air quality will deteriorate this afternoon due to forecasted traffic congestion and stagnant winds"). The current system has no predictive capability.

- **Health correlation blind spot**: Healthcare clients pay a premium for analysis connecting pollution exposure to health outcomes, but ClimaSense has never systematically joined their air quality data with hospital health incident records. Early analysis suggests strong correlations, but the data has never been integrated at scale.

- **Source attribution**: Environmental regulators want to know which emission sources (industrial facilities, highways, construction sites) contribute most to poor air quality at specific monitoring stations. This requires spatial analysis joining emission source locations with station readings and wind patterns.

## Available Data Sources

The following datasets are available in the project data repository:

| Source File | Format | Records | Description |
|---|---|---|---|
| `air-quality-readings.csv` | CSV | 800,000 | Station-level pollutant readings (PM2.5, PM10, ozone, NO2, SO2, CO) with AQI values, categories, and geographic coordinates |
| `weather-conditions.json` | JSON | 350,000 | Co-located weather observations: temperature, humidity, wind speed/direction, pressure, precipitation, and cloud cover |
| `traffic-counts.csv` | CSV | 250,000 | Road sensor data: vehicle counts, average speed, truck percentage, road type, and congestion level by city |
| `health-incidents.json` | JSON | 30,000 | Aggregated hospital records: respiratory ER visits, asthma admissions, and heat illness counts by city, date, and age group |
| `emission-sources.csv` | CSV | 20,000 | Registered emission source inventory: type, estimated annual tonnage, coordinates, and permit status by city |

## Business Questions

ClimaSense's clients and internal teams need answers to these questions:

1. **Traffic-pollution correlation**: How strongly do traffic volume and congestion levels correlate with air quality readings at nearby stations? Can rush-hour traffic patterns predict afternoon AQI levels?

2. **AQI spike prediction**: Using historical air quality data combined with weather forecasts (wind, temperature inversions, humidity), can the system predict AQI spikes 6 hours in advance with sufficient accuracy to issue proactive public health advisories?

3. **Source attribution**: For each monitoring station, which nearby emission sources (by type and distance) have the strongest measurable impact on pollutant readings? Does the relationship change with wind direction?

4. **Health outcome correlation**: Is there a statistically measurable relationship between daily AQI levels and respiratory emergency room visits? What is the lag time between a pollution spike and elevated health incidents? Which age groups are most affected?

5. **Seasonal and temporal patterns**: How do pollution levels vary by hour of day, day of week, and season across different cities? Are there predictable weekly cycles driven by commute patterns?

6. **Real-time spike detection**: Can the system detect rapid AQI deterioration (e.g., PM2.5 increasing by more than 50% within one hour) and issue alerts within minutes?

7. **Permit compliance**: Are there emission sources whose estimated output appears inconsistent with readings at nearby monitoring stations, suggesting possible permit violations or underreported emissions?

## Stage Guide

The following describes the **minimum floor** for each stage. Strong submissions will go well beyond these starting points.

### Stage 1: Data Lake Foundation (HDFS)

- Load all five data files into HDFS, preserving original formats
- Design HDFS zones: `raw/` for landing, `processed/` for cleaned/joined data, `analytics/` for final outputs
- The air-quality-readings file is the largest --- verify multi-block storage in HDFS
- Consider partitioning by city in processed zones, since most analysis is city-scoped

### Stage 2: Batch Transformation (Spark)

- **Clean**: Validate pollutant readings against physical limits (no negative concentrations); standardize timestamps across all sources to a common timezone or UTC; validate AQI category matches the computed AQI value
- **Join**: Link air-quality-readings with weather-conditions on station_id and timestamp to enable weather-adjusted pollution analysis. Join with traffic-counts by city and time window to correlate traffic with pollution. Spatially associate emission-sources with nearby monitoring stations (within a configurable radius).
- **Aggregate**: Compute daily and hourly AQI summaries by city. Compute rolling 24-hour pollution averages per station. Aggregate health incidents alongside daily city-level AQI for correlation analysis. Compute traffic-weighted pollution indices.
- Write analytical datasets to HDFS in Parquet format

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- Air quality sensor readings are the natural streaming source --- each station reports every 15 minutes
- Design a Kafka topic for sensor readings (station_id, timestamp, pm25, pm10, ozone, aqi_value, city)
- Use Spark Structured Streaming to maintain running hourly AQI averages per station and detect rapid deterioration
- Trigger alerts when AQI exceeds 150 (unhealthy threshold) or when PM2.5 increases by more than 50% compared to the previous hour's average

### Stage 4: Pipeline Orchestration (Airflow)

- Build a DAG that ingests daily batch data (new sensor readings, weather, traffic, health incidents), runs Spark transformations, and produces analytical outputs
- Include quality gates: verify that all 500 stations reported data (flag missing stations), check for sensor malfunction indicators (constant readings, impossible values), validate geographic coordinates
- Consider a branch structure: one path for pollution analytics, another for health correlation analysis, joining at a final city-level dashboard export
- The streaming alert pipeline runs continuously alongside the batch analytics DAG

## Evaluation Focus

A strong ClimaSense submission will demonstrate:

- **Multi-source integration** that connects environmental, transportation, health, and regulatory data --- the best insights emerge from these cross-domain joins
- **Spatial awareness** in the analysis --- emission source proximity, wind direction effects, and station-level granularity show sophisticated thinking
- **Time-series sophistication** --- rolling averages, lag analysis between pollution and health outcomes, and temporal patterns demonstrate analytical depth
- **A credible streaming design** for real-time pollution spike detection with meaningful alert thresholds
- **Actionable outputs** --- city-level dashboards, health advisories, and source attribution reports that clients would actually use
- **Robust Airflow DAG** with data quality gates appropriate for sensor data (missing stations, malfunction detection)

## Data Access

Download the datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/09-climasense-environment
```

Each team member should clone or download the data and place it in their project's `data/` directory before beginning pipeline development.
