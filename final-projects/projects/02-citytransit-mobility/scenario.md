# Final Project: MetroLink Transit — Urban Mobility Analytics

## Company Background

MetroLink Transit Authority is the primary public transportation provider for a major metropolitan area with a population of 3.2 million. The agency operates a multimodal network consisting of 450 buses across 62 routes, 3 light rail lines (Red, Blue, and Green) serving 45 stations, and a bike-share program with 5,000 bicycles distributed across 320 docking stations. MetroLink moves approximately 800,000 passengers per day during normal operations, making it the sixth-largest transit agency in the region.

The agency's ridership peaked in 2019 at 285 million annual trips. The pandemic caused a devastating 65% drop, and while ridership has recovered significantly, it remains 22% below pre-pandemic levels as of late 2025. The ridership decline has not been uniform — some routes and stations have fully recovered, while others remain well below their historical baselines. Remote work patterns have shifted commuter demand, with weekday morning rush-hour ridership down 30% but midday and weekend ridership actually exceeding 2019 levels on some routes. This creates a mismatch between MetroLink's fixed-schedule, rush-hour-centric service design and the actual demand patterns of its riders.

MetroLink's board of directors has approved a $15M "Smart Transit" initiative to use data analytics for route optimization, demand forecasting, and real-time service management. Your team has been engaged as the data engineering consultants to build the analytics platform that will power this initiative. The stakes are high — MetroLink's federal funding is partially tied to ridership metrics, and the agency needs to demonstrate it is making data-driven investments to maintain its funding levels.

## The Business Problem

MetroLink faces three interconnected challenges:

**Ridership Recovery Gap**: The 22% ridership shortfall translates to approximately **$48M in lost annual fare revenue**. Federal formula funding, which accounts for 40% of MetroLink's operating budget, is calculated partly on ridership — so the gap also threatens **$30M in federal funding** over the next 3 years. MetroLink needs to understand exactly where ridership is recovering, where it isn't, and why.

**Service-Demand Mismatch**: MetroLink's bus routes and schedules were designed in 2015 and have barely changed. Analysis suggests that **35% of bus service hours are deployed on routes where demand has shifted significantly**, either to different times of day or to different corridors entirely. Meanwhile, emerging demand corridors — particularly serving healthcare facilities and suburban employment centers — are underserved.

**Operational Inefficiency**: Bus bunching (where two buses on the same route arrive at a stop within minutes of each other, followed by a long gap) affects an estimated **28% of routes** during peak hours. This wastes fuel, frustrates passengers, and creates uneven loading where one bus is packed and the following one is nearly empty. MetroLink's dispatchers currently have no real-time visibility into bunching events.

The bike-share program adds another dimension — it was designed to solve the "last mile" problem, connecting transit stations to final destinations. But **40% of bike-share stations have either chronic oversupply or undersupply of bikes**, suggesting the station locations and rebalancing strategy need rethinking.

## Available Data Sources

| Source | Format | Records | Key Fields |
|--------|--------|---------|------------|
| Bus Telemetry | CSV | 1,300,000 | bus_id, route_id, timestamp, lat, lon, speed_mph, passenger_count, door_open_count, fuel_level_pct |
| Rail Ridership | JSON | 500,000 | station_id, timestamp, entries, exits, line, day_type |
| Bike-Share Trips | CSV | 200,000 | trip_id, start_station, end_station, start_time, end_time, duration_min, user_type, bike_id |
| Passenger Complaints | JSON | 20,000 | complaint_id, timestamp, route_id, category, severity, description_length |
| Weather Hourly | CSV | 50,000 | timestamp, temp_f, precipitation_in, wind_mph, condition |

### Data Notes

- **Bus Telemetry**: GPS pings every 30 seconds from each bus in service. The `passenger_count` is estimated from the automatic passenger counter (APC) system and may have ±10% accuracy. The `door_open_count` indicates how many times doors opened at stops.
- **Rail Ridership**: Collected from turnstile/tap-in systems at each station. Entries and exits are counted separately. The `day_type` distinguishes weekday, Saturday, and Sunday service schedules.
- **Bike-Share Trips**: Each record represents a completed trip. Duration and station data can help identify popular corridors and peak usage times. The `user_type` distinguishes annual subscribers from casual (single-ride) users.
- **Passenger Complaints**: Submitted through MetroLink's app and website. Categories include delay, overcrowding, safety, cleanliness, and driver behavior. Severity ranges from 1 (minor inconvenience) to 5 (service failure). The `description_length` field is a proxy for complaint detail.
- **Weather Hourly**: From the metro area's main weather station. Conditions include clear, cloudy, rain, heavy_rain, snow, and fog.

## Business Questions

MetroLink's executive team and board of directors need your analysis to address the following:

1. **Route Performance**: Which bus routes are significantly underperforming (low ridership relative to service hours), and which are overcrowded? Rank routes by a "performance index" that considers ridership, complaints, and schedule adherence.
2. **Ridership Patterns**: How have ridership patterns changed by time of day, day of week, and mode (bus vs. rail vs. bike-share)? Where are the emerging demand corridors that are currently underserved?
3. **Weather Impact**: How does weather affect ridership across the three modes? Do rainy days push bike-share users to bus/rail? What weather thresholds cause the biggest ridership drops?
4. **Bike-Share Optimization**: Which bike-share stations should be added, relocated, or removed based on trip patterns and proximity to transit stations? Which stations are most prone to empty-dock or full-dock problems?
5. **Bus Bunching Detection**: How prevalent is bus bunching across the network? Which routes and times of day are most affected? What is the downstream impact on passenger wait times and complaints?
6. **Multimodal Connections**: How well do bus schedules align with rail arrivals/departures? Are passengers making successful connections, or are they missing connections (inferred from ridership drop-off patterns)?
7. **Complaint Analysis**: Which routes and stations generate the most complaints? Is complaint severity correlated with specific operational metrics (delays, overcrowding)?

## Stage Guide

This section provides **minimum scaffolding** for each stage — think of these as the floor, not the ceiling. Strong projects will go well beyond these suggestions.

### Stage 1: Data Lake Foundation (HDFS)

- **Zone design**: Create landing, curated, and analytics zones in HDFS
- **Landing zone**: Load all five data sources in their original formats
- **Format considerations**: Bus telemetry is the largest dataset and benefits most from Parquet conversion. Rail ridership JSON should be flattened and converted.
- **Partitioning hints**: Bus telemetry could be partitioned by `route_id` or by date. Rail ridership partitions well by `line` and `day_type`. Bike-share trips could partition by month.
- **Replication**: Standard replication for all sources. Consider higher replication for complaint data if used for regulatory reporting.

### Stage 2: Batch Transformation (Spark)

- **Key joins**: Enrich bus telemetry with weather data (join on timestamp hour). Join complaints with bus telemetry to correlate operational metrics with complaint spikes. Combine rail ridership with bike-share trips near rail stations to analyze multimodal patterns.
- **Aggregations**: Hourly/daily ridership by route and station. Average speed by route and time of day (to identify chronic congestion). Bike-share station utilization rates.
- **Derived features**: Calculate headway (time between consecutive buses on the same route at the same stop) from telemetry data. Compute "dwell time" at stops from door_open events. Calculate bike-share station turnover rates.
- **Output**: Write curated datasets as Parquet, partitioned by route and date. Build analytics-ready tables for route performance dashboards.

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- **Streaming source**: Bus GPS telemetry is the natural streaming source — every 15 seconds in production.
- **Kafka topic design**: Consider a `bus-gps` topic keyed by `route_id` and a `transit-alerts` topic for detected events.
- **Real-time logic**: Detect bus bunching — when two buses on the same route are within 200 meters of each other (use the Haversine formula or simple lat/lon distance). Use a sliding window (e.g., 5 minutes) to track bus positions.
- **Alert events**: Generate bunching alerts with route_id, bus_ids, location, and timestamp. Optionally, detect buses that have been stationary for too long (possible breakdown).
- **Architecture decision**: Consider whether real-time bus monitoring benefits from a Lambda architecture (historical analysis + real-time tracking) or Kappa architecture.

### Stage 4: Pipeline Orchestration (Airflow)

- **Batch DAG**: Schedule daily batch processing. Tasks: ingest new telemetry/ridership data, run Spark transforms, generate route performance metrics, run quality checks, write to analytics zone.
- **Quality gates**: Validate GPS coordinates are within the metro area bounding box. Check that passenger counts are non-negative. Verify that the count of records per route per day is within expected ranges.
- **Monitoring DAG**: Monitor the streaming pipeline — check Kafka consumer lag, verify alert generation rates.
- **Retry and SLA**: Set SLAs for daily batch completion. Add retries for Spark tasks.

## Evaluation Focus

Strong submissions for this project will demonstrate:

- **Spatial awareness**: Transit data is inherently geographic. Projects that incorporate spatial analysis (even simple distance calculations) will produce more meaningful insights than those that ignore location.
- **Temporal pattern recognition**: The value of this dataset lies in how patterns shift across time — rush hour vs. midday, weekday vs. weekend, pre- vs. post-pandemic. Drill into these temporal dimensions.
- **Multimodal integration**: MetroLink operates three modes. The most interesting insights come from understanding how they interact — do bike-share trips feed rail stations? Do bus delays ripple into rail ridership?
- **Actionable recommendations**: Frame your findings as specific service changes MetroLink could make — "Route 42 should shift 2 buses from the 7-8 AM window to 11 AM-1 PM based on demand analysis" is far more useful than "ridership patterns have changed."

## Data Access

Download the project datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/02-citytransit-mobility
```

All data files are gzip-compressed (`.csv.gz` and `.json.gz`). Decompress them after downloading with `gunzip *.gz` or load them directly in Spark (which reads gzipped files natively). Clone the data repo and copy files into your project's `data/` directory, or reference them directly from HDFS after loading.
