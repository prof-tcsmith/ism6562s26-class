# Final Project: MediaWave Streaming — Video Platform Analytics

## Company Background

MediaWave is a video streaming platform that has grown from a niche indie film service to a mainstream competitor with 8 million paid subscribers across three plan tiers: Basic ($8.99/month), Standard ($13.99/month), and Premium ($19.99/month with 4K access). The platform licenses a catalog of 20,000 titles spanning movies, series, documentaries, and live events, at a total annual content licensing cost of $500M. MediaWave competes for subscribers against larger incumbents by focusing on curated niche content --- international cinema, independent documentaries, and cult classics --- and by offering a "no algorithm bubble" recommendation philosophy that promises to surface genuinely diverse content rather than recycling the same popular titles.

Despite this differentiated positioning, MediaWave is losing money. Monthly churn sits at 4.2%, meaning the company replaces roughly 336,000 subscribers every month just to stay flat. Customer acquisition costs have risen to $45 per subscriber, so every churned subscriber represents not just lost recurring revenue but wasted marketing spend. The content team suspects that 30% of the catalog is watched by fewer than 100 unique users per month, yet those titles collectively cost $80M annually to license. Meanwhile, the platform's recommendation engine --- built three years ago as a simple collaborative filter --- has a click-through rate of just 12%, well below the industry average of 25%. Users report that they spend more time browsing than watching, and "recommendation fatigue" is cited in 18% of cancellation surveys.

The fundamental problem is that MediaWave is drowning in behavioral data it does not use. The platform logs every browse, search, play, pause, skip, and rating event --- roughly 15 million interactions per day --- but these logs sit in compressed files on an aging server cluster that nobody outside the engineering team can access. Viewing history, user profiles, content metadata, and streaming quality metrics each live in different systems with different schemas. The CEO has mandated a "data-first" initiative: build a unified analytics pipeline that connects user behavior to content performance to streaming quality, enabling data-driven decisions about which content to license, which users to target for retention campaigns, and how to overhaul the recommendation engine. The stakes are existential --- at the current churn rate, MediaWave has 18 months of runway before subscriber losses outpace growth.

## The Business Problem

MediaWave faces interconnected challenges across retention, content strategy, and platform quality:

- **Churn hemorrhage**: At 4.2% monthly churn (336,000 subscribers/month), MediaWave spends $15M/month on acquisition just to maintain its subscriber base. The company cannot identify at-risk subscribers until they cancel, because behavioral signals (declining watch time, fewer logins, more buffering frustrations) are trapped in unanalyzed log files.

- **Content ROI opacity**: $500M in annual licensing costs with no systematic way to measure which titles drive new subscriptions, which retain existing subscribers, and which are essentially dead weight. Content acquisition decisions are based on genre gut feel rather than data.

- **Recommendation failure**: The current recommendation engine has a 12% click-through rate (vs. 25% industry average). Users who do not find something to watch within 90 seconds of browsing are 3x more likely to close the app. Improving recommendations could directly reduce churn.

- **Streaming quality impact**: Buffering events and resolution drops are correlated with cancellation in preliminary analysis, but the relationship has never been quantified. The infrastructure team suspects that certain ISP and CDN region combinations produce consistently poor experiences, but cannot prove it without joining quality data with user behavior data.

- **Plan tier optimization**: MediaWave does not know whether Premium subscribers watch meaningfully more 4K content than Standard subscribers, or whether Basic plan limitations (SD only, single device) drive churn. Pricing and tier structure changes are made without data.

## Available Data Sources

The following datasets are available in the project data repository:

| Source File | Format | Records | Description |
|---|---|---|---|
| `viewing-history.csv` | CSV | 700,000 | Individual viewing sessions: user, content, timestamps, duration watched vs total duration, completion percentage, device, and quality level |
| `content-catalog.json` | JSON | 20,000 | Full content catalog with genres, release year, duration, rating, language, origin country, monthly license cost, and IMDb score |
| `user-profiles.csv` | CSV | 200,000 | Subscriber records: signup date, plan type, demographics, device count, monthly watch hours, last login, and churn flag |
| `user-interactions.json` | JSON | 550,000 | Granular behavioral events: browse, search, play, pause, skip, rate, add-to-watchlist, and share actions with timestamps and context |
| `streaming-quality.csv` | CSV | 200,000 | Technical quality metrics per session: buffering events, bitrate, resolution changes, latency, CDN region, and ISP |

## Business Questions

MediaWave's leadership team needs answers to these questions:

1. **Churn prediction**: Which behavioral signals best predict subscriber churn 30 days in advance? Can the system identify at-risk users early enough for targeted retention campaigns (personalized recommendations, discount offers, content highlights)?

2. **Content ROI analysis**: Which titles and genres drive the most viewing hours per licensing dollar? Are there titles that are rarely watched but whose viewers have significantly lower churn rates (i.e., "anchor content" that keeps specific subscriber segments loyal)?

3. **Recommendation improvement**: What viewing patterns, search queries, and genre preferences can be extracted to improve content recommendations? Do users who interact with recommendations (vs. using search) have higher engagement and lower churn?

4. **Streaming quality and churn**: Is there a quantifiable relationship between buffering events, resolution drops, and subscriber churn? Which CDN region and ISP combinations produce the worst user experience, and what is the estimated revenue impact?

5. **Completion patterns**: What content characteristics (genre, duration, IMDb score, release year) predict high completion rates? Do users who complete content at higher rates churn less?

6. **Plan tier behavior**: Do Premium subscribers actually use 4K streaming proportionally to the price premium they pay? Are Basic plan limitations (lower quality, fewer devices) a significant churn driver for that tier?

7. **Real-time engagement monitoring**: Can the system detect trending content (rapid concurrent viewer spikes) in real-time to inform CDN scaling decisions and homepage promotion?

## Stage Guide

The following describes the **minimum floor** for each stage. Strong submissions will go well beyond these starting points.

### Stage 1: Data Lake Foundation (HDFS)

- Load all five data files into HDFS, preserving original formats
- Design HDFS zones: `raw/` for landing, `processed/` for cleaned/joined data, `analytics/` for final outputs
- The viewing-history and user-interactions files are largest --- verify multi-block storage
- Consider whether partitioning by date or by content_id would benefit downstream analysis

### Stage 2: Batch Transformation (Spark)

- **Clean**: Validate viewing durations (duration_watched should not exceed total_duration); standardize device categories; handle null search queries in interactions; ensure completion_pct is between 0 and 100
- **Join**: Link viewing-history with content-catalog on content_id to attach genre, license cost, and ratings to viewing sessions. Join with user-profiles on user_id to connect behavior with subscription tier and churn status. Join viewing sessions with streaming-quality on session_id to correlate technical quality with viewing behavior.
- **Aggregate**: Compute per-user monthly engagement metrics (total watch hours, unique titles, completion rate, interaction count). Compute per-content performance metrics (unique viewers, total hours, avg completion, cost-per-viewing-hour). Aggregate streaming quality by CDN region and ISP.
- Write analytical datasets to HDFS in Parquet format

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- User interaction events are the natural streaming source --- browse, play, pause, skip, and search events flow continuously
- Design a Kafka topic for user activity events (user_id, timestamp, action, content_id, device)
- Use Spark Structured Streaming to track concurrent viewers per content title and detect trending spikes
- Trigger alerts when buffering events exceed 3 per session (poor experience flag) or when a title's concurrent viewers increase by more than 200% in a 15-minute window (trending content requiring CDN scaling)

### Stage 4: Pipeline Orchestration (Airflow)

- Build a DAG that ingests daily viewing, interaction, and quality data into HDFS, runs Spark transformations, updates engagement metrics and churn risk scores, and exports analytical reports
- Include quality gates: verify user_ids in viewing history exist in user profiles, check for impossible viewing durations, validate that content_ids reference the catalog
- Consider separate DAG paths for content analytics vs user analytics, merging at a combined churn-risk scoring task
- The streaming pipeline for real-time engagement monitoring runs continuously alongside the batch DAG

## Evaluation Focus

A strong MediaWave submission will demonstrate:

- **User-centric analytics** that tell the story of subscriber behavior from signup through engagement (or disengagement) to churn or retention
- **Content ROI calculations** that connect licensing costs to actual viewership value --- this is the analysis that would most directly impact a $500M budget
- **Churn modeling** that identifies actionable behavioral thresholds (e.g., "users who watch fewer than 2 hours in a 14-day window have 5x churn risk")
- **Quality-experience linkage** showing how technical issues translate to business outcomes
- **A realistic streaming design** for monitoring platform health and content trending in real-time
- **Well-orchestrated Airflow DAG** with logical dependencies and quality gates that reflect real platform data challenges

## Data Access

Download the datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/10-mediawave-streaming
```

Each team member should clone or download the data and place it in their project's `data/` directory before beginning pipeline development.
