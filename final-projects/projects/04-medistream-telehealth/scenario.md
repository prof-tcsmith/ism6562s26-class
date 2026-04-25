# Final Project: MediStream — Telehealth Platform Analytics

## Company Background

MediStream is a telehealth startup founded in 2021, at the height of pandemic-driven virtual care adoption. In just four years, the company has grown to a network of 800 physicians spanning 15 medical specialties, serving over 500,000 registered patients. MediStream's platform enables video consultations, remote vitals monitoring (through integrations with consumer wearable devices), electronic prescribing, and follow-up care coordination. The company processes approximately 3,000 appointments per day and has facilitated over 2 million consultations since launch.

MediStream's rapid growth was fueled by consumer demand and insurance reimbursement parity for virtual visits. However, that growth came at a cost — the platform was built quickly, with separate engineering teams building the appointment scheduling system, the electronic health records (EHR) module, the video conferencing infrastructure, the patient feedback system, and the physician management tools. Each system has its own database, its own data model, and its own reporting dashboard. There is no unified view of the patient journey, no way to correlate session quality with patient satisfaction, and no systematic analysis of physician performance across scheduling, clinical, and patient experience dimensions.

MediStream's Chief Medical Officer and Chief Technology Officer have jointly sponsored a "Data Unification" initiative. Your team has been brought in as data engineering consultants to build a unified analytics platform that connects the dots across MediStream's fragmented data landscape. The company's Series C funding round is approaching, and investors will scrutinize operational metrics — the executive team needs a clear, data-backed picture of MediStream's operational health and the levers available to improve it.

## The Business Problem

MediStream faces four interconnected operational challenges:

**High No-Show Rate**: The current appointment no-show rate is **18%**, meaning nearly one in five scheduled consultations does not occur. Each no-show represents lost revenue (the physician's time slot is wasted), delayed patient care, and inefficient resource allocation. At an average reimbursement of $120 per visit, the no-show problem costs MediStream approximately **$23M in annual lost revenue**. Worse, the no-show rate varies dramatically by specialty, time of day, and patient demographics — but MediStream cannot identify these patterns because appointment data isn't linked to patient history or session data.

**Video Quality Complaints**: Approximately **15% of completed sessions** experience significant video quality degradation — buffering, pixelation, audio dropouts, or disconnections. These technical issues directly impact clinical outcomes (physicians may miss visual symptoms) and patient satisfaction. MediStream's NPS (Net Promoter Score) drops from 72 for technically smooth sessions to 31 for sessions with quality issues. However, the session quality data (latency, packet loss, resolution) has never been systematically correlated with patient feedback to understand which technical thresholds actually matter to patients.

**Physician Utilization Imbalance**: MediStream's 800 physicians have wildly uneven workloads. The top 10% of physicians (by volume) handle **35% of all appointments**, while the bottom 20% have **40% unfilled capacity**. Some of this reflects patient preference and specialty demand, but much of it stems from poor scheduling algorithms that don't account for physician availability patterns, specialty matching, or geographic time zones. Overburdened physicians report burnout and shorter appointment times, while underutilized physicians churn to competing platforms.

**Fragmented Patient Journey**: Without a unified data platform, MediStream cannot answer basic questions like: "What percentage of patients with a follow-up recommendation actually book and complete that follow-up?" or "Do patients who report wearable vitals before their appointment have shorter, more efficient consultations?" These cross-system insights require joining appointment, vitals, session quality, and feedback data — exactly what MediStream's current infrastructure cannot do.

## Available Data Sources

| Source | Format | Records | Key Fields |
|--------|--------|---------|------------|
| Appointments | CSV | 550,000 | appointment_id, patient_id, physician_id, scheduled_time, actual_start, actual_end, specialty, status, wait_time_min, visit_type |
| Patient Vitals | JSON | 400,000 | patient_id, timestamp, measurement_type, value, unit, device_type |
| Session Quality | CSV | 250,000 | session_id, appointment_id, video_resolution, audio_quality_score, latency_ms, packet_loss_pct, duration_sec, device_type, os |
| Patient Feedback | JSON | 50,000 | feedback_id, appointment_id, patient_id, rating, categories_mentioned, nps_score |
| Physician Schedule | CSV | 30,000 | physician_id, date, start_time, end_time, specialty, max_appointments, actual_appointments |

### Data Notes

- **Appointments**: Each record represents a scheduled appointment. The `status` field indicates completed, cancelled (cancelled in advance), or no_show (patient did not attend without cancelling). The `wait_time_min` is the time between the scheduled start and the physician actually joining the video call. Visit types include initial (first visit with this physician), followup, and urgent.
- **Patient Vitals**: Measurements submitted by patients, either manually or via wearable device integration. Blood pressure entries have nested systolic/diastolic values under a `reading` key. Device types distinguish between manual entry, wearable sync (Fitbit, Apple Watch, etc.), and clinic-reported values.
- **Session Quality**: Technical metrics recorded during the video session. Only exists for completed appointments. The `audio_quality_score` is computed by MediStream's codec (1 = terrible, 10 = perfect). Resolution values include 240p, 480p, 720p, and 1080p.
- **Patient Feedback**: Post-appointment surveys completed by approximately 12% of patients. The `categories_mentioned` is an array of tags the patient selected (e.g., wait_time, physician_manner, technical_issues, prescription_clarity). The NPS score (0–10) indicates likelihood to recommend MediStream.
- **Physician Schedule**: Daily schedule blocks for each physician. The gap between `max_appointments` and `actual_appointments` indicates unused capacity.

## Business Questions

MediStream's executive team needs your analysis to address the following:

1. **No-Show Prediction**: What factors predict appointment no-shows? Build a risk profile based on patient history, appointment characteristics (time of day, day of week, specialty, visit type), and wait time patterns. Which patient segments have the highest no-show rates?
2. **Session Quality Impact**: At what thresholds do technical metrics (latency, packet loss, resolution) significantly impact patient satisfaction? Is there a "good enough" quality level above which further improvements don't matter?
3. **Physician Performance**: Which physicians consistently receive low ratings, and is this driven by clinical factors (short appointment times, lack of follow-up) or technical factors (poor video quality due to the physician's setup)? Separate physician-attributable issues from platform-attributable issues.
4. **Appointment Duration Prediction**: Can we predict how long an appointment will take based on specialty, visit type, patient history, and whether vitals were submitted in advance? This would allow smarter scheduling.
5. **Vitals and Outcomes**: Do patients who submit vitals before their appointment have shorter consultations, higher satisfaction scores, or better follow-up rates? Should MediStream incentivize pre-visit vitals submission?
6. **Scheduling Optimization**: What is the optimal number of appointments per physician per day by specialty, balancing utilization, patient satisfaction, and appointment duration? Where are the biggest scheduling gaps?
7. **Platform Reliability**: Which device types (phone, tablet, laptop) and operating systems have the worst session quality? Should MediStream recommend specific technical requirements to patients before their appointment?

## Stage Guide

This section provides **minimum scaffolding** for each stage — think of these as the floor, not the ceiling. Strong projects will go well beyond these suggestions.

### Stage 1: Data Lake Foundation (HDFS)

- **Zone design**: Create landing, curated, and analytics zones in HDFS
- **Landing zone**: Load all five data sources in their original formats
- **Format considerations**: Patient vitals JSON with nested blood pressure readings requires flattening during Parquet conversion. Appointments CSV is straightforward but large.
- **Partitioning hints**: Appointments could partition by `specialty` and month. Session quality could partition by `device_type`. Patient vitals could partition by `measurement_type`.
- **Replication**: Higher replication for patient vitals and appointments (HIPAA-relevant data in a real scenario). Standard replication for session quality and schedules.

### Stage 2: Batch Transformation (Spark)

- **Key joins**: Join appointments with session quality (on appointment_id) to correlate technical metrics with appointment outcomes. Join appointments with patient feedback to link satisfaction to operational metrics. Join appointments with physician schedules to calculate utilization rates.
- **Aggregations**: No-show rates by specialty, time of day, day of week, and visit type. Average session quality metrics by device type and OS. Physician utilization rates (actual vs. max appointments) by day and specialty.
- **Derived features**: Calculate "appointment history score" for each patient (ratio of completed to scheduled appointments). Compute physician "quality-adjusted volume" (appointments weighted by patient ratings). Flag sessions where quality dropped below thresholds during the appointment.
- **Output**: Write curated datasets as Parquet with appropriate partitioning. Build analytics tables for no-show prediction features and physician performance dashboards.

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- **Streaming source**: Session quality metrics are the natural streaming source — they stream in real-time during active appointments.
- **Kafka topic design**: Consider a `session-metrics` topic keyed by `session_id` and a `session-alerts` topic for quality degradation events.
- **Real-time logic**: Monitor active sessions and alert when latency exceeds 500ms or packet loss exceeds 5%. Use a sliding window (e.g., 2-minute) to track quality trends — alert when quality is consistently degrading rather than on single-point spikes.
- **Alert events**: Generate alerts with session_id, appointment_id, physician_id, alert type (high_latency/packet_loss/low_resolution), current metrics, and suggested action (e.g., "suggest switching to audio-only").
- **Architecture decision**: Real-time session monitoring clearly benefits from a streaming-first approach. Consider whether appointment analytics (no-show prediction, scheduling) can also be served from streaming data or if batch reprocessing adds value.

### Stage 4: Pipeline Orchestration (Airflow)

- **Batch DAG**: Schedule daily processing of the previous day's completed appointments. Tasks: ingest new appointment, feedback, and vitals data; run Spark transforms; update physician performance metrics; run quality checks; refresh analytics tables.
- **Quality gates**: Validate that appointment records have consistent status values. Check that session quality records exist for all completed appointments. Verify feedback NPS scores are within the 0–10 range. Flag anomalies like physicians with >30 appointments in a single day.
- **Monitoring DAG**: Monitor the session quality streaming pipeline. Check for stale data (sessions that should have quality data but don't). Verify alert generation rates.
- **Retry and SLA**: Set SLAs for daily batch processing. Build a weekly "physician performance report" DAG that aggregates weekly metrics.

## Evaluation Focus

Strong submissions for this project will demonstrate:

- **Patient journey thinking**: The most valuable insights come from tracing the patient journey across all five data sources — from scheduling through vitals submission, to the appointment itself, to session quality, to post-visit feedback. Projects that maintain this end-to-end perspective will stand out.
- **Actionable segmentation**: "The no-show rate is 18%" is a starting point, not a finding. "Urgent-care appointments scheduled for Monday mornings have a 32% no-show rate, while follow-up appointments on Tuesday-Thursday afternoons have only 8%" is actionable intelligence.
- **Technical-clinical correlation**: The unique aspect of this dataset is the ability to correlate technical metrics (video quality) with clinical outcomes (satisfaction, follow-up rates). Explore these relationships deeply.
- **Physician-friendly recommendations**: Frame physician performance insights carefully — the goal is to help physicians succeed, not to create a punitive ranking. Distinguish between factors within the physician's control and platform-level issues.

## Data Access

Download the project datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/04-medistream-telehealth
```

All data files are gzip-compressed (`.csv.gz` and `.json.gz`). Decompress them after downloading with `gunzip *.gz` or load them directly in Spark (which reads gzipped files natively). Clone the data repo and copy files into your project's `data/` directory, or reference them directly from HDFS after loading.
