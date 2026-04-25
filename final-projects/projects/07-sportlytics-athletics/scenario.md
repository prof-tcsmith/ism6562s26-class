# Final Project: Sportlytics Athletics — Professional Basketball Analytics

## Company Background

Sportlytics is a sports analytics firm that provides data-driven insights to a professional basketball league comprising 30 teams and over 450 active players. Founded in 2019 by a group of former sports scientists and data engineers, Sportlytics has positioned itself as the league's premier analytics partner. Every arena is equipped with optical tracking cameras that capture player positions 25 times per second during games, producing terabytes of raw spatial data each season. Teams pay Sportlytics for processed insights --- fatigue models, injury risk scores, lineup optimization recommendations, and post-game performance breakdowns --- that inform coaching decisions worth millions of dollars in player contracts and game outcomes.

Despite the richness of their data, Sportlytics is struggling with scale. Their current analytics pipeline was built for a proof-of-concept with three teams and has not been re-architected since. Player tracking data is processed in nightly batch jobs that frequently fail when game volumes spike during the playoffs. Injury prediction models run on a single server and take 14 hours to retrain, meaning coaches receive stale risk assessments. Worst of all, the in-game analytics dashboard --- which was supposed to deliver real-time exertion monitoring during live games --- has a 45-second lag that makes it useless for real-time substitution decisions. Three teams have threatened to cancel their contracts unless Sportlytics can deliver sub-second in-game alerts and next-day batch reports that actually arrive by morning.

The CTO has greenlit a complete infrastructure overhaul built on distributed storage and processing. The new platform must handle the full historical archive (five seasons of tracking data), integrate it with game statistics, injury history, and training load data, and support both next-day batch analytics and real-time in-game monitoring. The stakes are high: the league's collective bargaining agreement now requires teams to track and report player workload data, meaning Sportlytics' platform will become a league-wide compliance tool in addition to a competitive advantage.

## The Business Problem

Sportlytics faces interconnected technical and business challenges:

- **Player injury costs**: Teams in the league collectively lost $780M in player salary to injured-list time last season. Sportlytics' current injury prediction model has a recall of only 38% --- it misses nearly two-thirds of injuries that could potentially be mitigated through workload management.

- **In-game latency**: The current tracking data pipeline has a 45-second processing lag during live games. Coaches need sub-5-second alerts when a player's cumulative exertion crosses fatigue thresholds so they can make timely substitution decisions.

- **Back-to-back fatigue**: Teams playing on consecutive nights (back-to-backs) see a measurable performance decline, but the magnitude varies dramatically by player. Currently, rest decisions are based on coach intuition rather than personalized fatigue models.

- **Training load optimization**: There is no integrated view connecting practice intensity, gym workouts, recovery sessions, sleep data, and game performance. Athletic trainers want evidence-based guidance on optimal training-to-rest ratios for individual players.

- **Travel impact**: The league spans multiple time zones, and some teams travel over 50,000 miles per season. Sportlytics suspects that travel distance and rest days interact with fatigue, but this has never been systematically analyzed.

## Available Data Sources

The following datasets are available in the project data repository:

| Source File | Format | Records | Description |
|---|---|---|---|
| `player-tracking.csv` | CSV | 750,000 | In-game spatial tracking data: court position, speed, acceleration, distance covered, and heart rate per timestamp |
| `game-stats.json` | JSON | 300,000 | Traditional box score statistics per player per quarter: points, rebounds, assists, shooting percentages, plus-minus |
| `injury-reports.csv` | CSV | 15,000 | Historical injury records: type, severity, games missed, treatment, and return timeline |
| `training-sessions.json` | JSON | 150,000 | Practice, gym, recovery, and film session logs with intensity scores, biometrics, and prior-night sleep data |
| `team-schedules.csv` | CSV | 10,000 | Full league schedule with venues, travel distances, rest days, back-to-back flags, and game results |

## Business Questions

Sportlytics' clients --- the 30 league teams --- need answers to these questions:

1. **Injury risk prediction**: Can historical workload patterns (cumulative distance, training intensity, sleep, travel) predict which players are at elevated injury risk in the next 7 days? Which features are most predictive?

2. **Fatigue-performance correlation**: How does cumulative exertion (total distance, high-speed sprints, minutes played) over a rolling 5-game window correlate with shooting percentage and plus-minus? At what workload threshold does performance decline become statistically significant?

3. **Back-to-back impact**: Quantify the average performance decline on the second night of a back-to-back. Which player profiles (age, position, season workload) are most affected, and which are resilient?

4. **Travel and rest interaction**: Does travel distance compound fatigue beyond what rest days alone account for? Are west-to-east trips more detrimental than east-to-west?

5. **Training load optimization**: What is the optimal ratio of practice-to-recovery sessions for maintaining peak game performance? Do players who exceed a weekly intensity threshold show declining game performance?

6. **Real-time exertion monitoring**: During live games, can the system detect when a player's heart rate or cumulative distance exceeds personalized fatigue thresholds and alert the coaching staff within seconds?

## Stage Guide

The following describes the **minimum floor** for each stage. Strong submissions will go well beyond these starting points.

### Stage 1: Data Lake Foundation (HDFS)

- Load all five data files into HDFS, preserving original formats
- Design HDFS zones: consider `raw/`, `processed/`, and `analytics/` layers
- The player-tracking file is the largest and should span multiple HDFS blocks --- verify this
- Consider partitioning strategies (by team_id, by game_id) that would improve downstream query performance

### Stage 2: Batch Transformation (Spark)

- **Clean**: Standardize timestamps across tracking and game data; validate heart rate ranges (reasonable bounds: 60--220 BPM); handle any missing fields in injury reports
- **Join**: Link player-tracking data with game-stats on game_id and player_id to connect spatial exertion with box score outcomes. Join training-sessions with team-schedules to compute workload context (days since last game, travel distance before session).
- **Aggregate**: Compute rolling 5-game workload summaries per player (total distance, avg heart rate, total minutes). Compute per-player back-to-back performance differentials. Aggregate injury frequency by player demographics and workload tier.
- Write analytical datasets to HDFS in Parquet format

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- Player tracking data is the natural streaming source --- in production it arrives at 25 frames per second during live games
- Design a Kafka topic for real-time player telemetry (game_id, player_id, timestamp, speed, heart_rate, cumulative_distance)
- Use Spark Structured Streaming to maintain running per-player exertion metrics
- Trigger alerts when heart rate exceeds 95% of a player's known max or when cumulative distance exceeds their fatigue threshold (derived from historical data)

### Stage 4: Pipeline Orchestration (Airflow)

- Build a DAG for the nightly batch pipeline: ingest new game data into HDFS, run Spark transformations, update rolling workload summaries, refresh injury risk scores
- Include quality gates: verify tracking data completeness (every player in the box score should have tracking records), check for physiologically impossible values
- Consider a separate DAG for weekly model retraining (if implementing SparkML)
- The streaming pipeline runs independently but the DAG should verify that the streaming checkpoint is healthy

## Evaluation Focus

A strong Sportlytics submission will demonstrate:

- **Domain-appropriate feature engineering** --- rolling workload windows, back-to-back flags, and travel-adjusted rest metrics show analytical sophistication
- **Meaningful integration of all five data sources** --- the best insights come from combining tracking, game stats, injury history, training, and schedule data
- **Realistic streaming design** --- even if the Kafka producer simulates data rather than processing true 25fps streams, the architecture should be sound
- **Quantified business answers** --- "performance declines by X% on back-to-backs for players over age 30" is far stronger than "we joined the tables"
- **Clean Airflow DAG** with logical task dependencies reflecting the natural data flow from raw ingestion through transformation to analytics

## Data Access

Download the datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/07-sportlytics-athletics
```

Each team member should clone or download the data and place it in their project's `data/` directory before beginning pipeline development.
