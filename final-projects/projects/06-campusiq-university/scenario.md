# Final Project: CampusIQ University — Data-Driven Higher Education

## Company Background

CampusIQ is a large public research university serving approximately 45,000 students across 200 degree programs, supported by 3,000 faculty members and a sprawling campus of 150 buildings. Founded in 1965, the university has grown from a small regional college into a nationally ranked institution. Over the past decade, enrollment has surged by 30%, but the administrative infrastructure --- spreadsheets managed independently by each department, siloed student information systems, and manual reporting processes --- has not kept pace. The provost's office receives critical enrollment and retention reports weeks after they are needed, and decisions about course scheduling, facility investments, and financial aid allocation are made largely on institutional inertia rather than evidence.

The situation reached a tipping point last year when the university's six-year graduation rate dropped below the benchmark set by its accrediting body. An internal audit revealed that 22% of students who left cited poor course availability as a primary reason --- they simply could not get the courses they needed to graduate on time. Meanwhile, campus facilities data showed that some buildings operated at 15% average occupancy while others had students sitting on hallway floors. The Board of Trustees has mandated a university-wide data initiative, and the CIO has been given 18 months to deliver an integrated analytics platform that can guide decisions from the provost level down to individual academic advisors.

CampusIQ's data landscape is a microcosm of institutional complexity. Student academic records span 15 years of history across three different student information systems. The learning management system (LMS) captures granular engagement data --- every login, assignment submission, and discussion post --- but it has never been integrated with academic records. Building access systems, HVAC sensors, and dining swipe data all exist in separate databases maintained by different departments. The challenge is not just volume (tens of millions of records) but variety: CSV exports from legacy systems, JSON logs from modern web platforms, and sensor streams from IoT devices across campus. Building a unified data pipeline is the first step toward becoming a truly data-driven university.

## The Business Problem

CampusIQ faces several quantifiable pain points that demand an integrated data solution:

- **Retention crisis**: The university loses approximately 2,800 students per year to voluntary withdrawal, costing an estimated $42M in lost tuition revenue. Academic advisors currently have no early-warning system and rely on midterm grade reports that arrive too late to intervene effectively.

- **Scheduling inefficiency**: Over 1,200 course sections run below 50% capacity each semester, while 350 sections have waitlists exceeding 20 students. The registrar's office uses a decade-old scheduling algorithm that does not account for student demand patterns.

- **Facility waste**: The university spends $18M annually on building operations (HVAC, lighting, maintenance). Preliminary estimates suggest that 25--30% of this cost is attributable to heating, cooling, and lighting underutilized spaces.

- **Engagement blindspot**: The LMS generates 2 million events per week, but no one analyzes the data. Early research at peer institutions shows that declining LMS engagement is a stronger predictor of dropout than GPA alone.

- **Financial aid misallocation**: $120M in institutional aid is distributed using a formula last updated in 2015. The provost suspects that targeted redistribution could improve retention by 5--8% without increasing the total aid budget.

## Available Data Sources

The following datasets are available in the project data repository:

| Source File | Format | Records | Description |
|---|---|---|---|
| `student-records.csv` | CSV | 750,000 | Multi-semester academic records including grades, GPA, major, standing, enrollment status, and financial aid flag |
| `course-catalog.json` | JSON | 50,000 | Course section details: department, instructor, schedule, room assignment, enrollment and waitlist counts |
| `campus-facilities.csv` | CSV | 400,000 | Timestamped building/room sensor readings: occupancy, HVAC energy, lighting energy, and facility type |
| `student-engagement.json` | JSON | 550,000 | Student interaction events from LMS, library, tutoring, dining, and campus organizations with timestamps and durations |
| `financial-data.csv` | CSV | 200,000 | Per-student semester financial records: tuition charges, payments, aid amounts, balances, and scholarship type |

## Business Questions

The provost's office and academic leadership need the following questions answered:

1. **Retention prediction**: Which students are at highest risk of not returning next semester? What combination of academic performance, engagement patterns, and financial factors best predicts attrition?

2. **Course demand optimization**: Which courses are chronically under-supplied (long waitlists) and which are over-supplied (low enrollment)? How many additional sections of high-demand courses would eliminate waitlists?

3. **Facility utilization**: Which buildings and room types are most underutilized? What is the potential energy cost savings if underutilized spaces were consolidated or scheduled more efficiently?

4. **Engagement-success correlation**: Is there a measurable relationship between LMS engagement frequency, tutoring visits, and academic outcomes? At what engagement threshold does dropout risk increase significantly?

5. **Financial aid effectiveness**: Which scholarship types and aid levels have the strongest correlation with student persistence? Are there student segments where additional aid would yield disproportionate retention improvements?

6. **Scheduling-retention link**: Do students who are unable to enroll in required courses (evidenced by waitlists in major-required sections) have higher dropout rates than those who get their preferred schedule?

7. **Real-time facility monitoring**: Can the university detect and respond to building overcrowding events in near real-time, improving both safety and student experience?

## Stage Guide

The following describes the **minimum floor** for each stage. Strong submissions will go well beyond these starting points.

### Stage 1: Data Lake Foundation (HDFS)

- Load all five data files into HDFS, preserving their original formats (CSV stays CSV, JSON stays JSON)
- Design a zone structure in HDFS --- consider at minimum a `raw/` landing zone and a `processed/` zone for transformed outputs
- Verify that larger files (student-records, campus-facilities, student-engagement) span multiple HDFS blocks
- Document the HDFS directory layout and explain zone purpose

### Stage 2: Batch Transformation (Spark)

- **Clean**: Handle any null or malformed records; standardize date formats; ensure consistent categorical values (e.g., enrollment_status, class_standing)
- **Join**: Link student-records with financial-data on student_id and semester to create a unified student profile. Join engagement events with academic records to correlate activity with performance.
- **Aggregate**: Compute per-student semester summaries (total engagement hours, GPA trend, financial balance). Compute per-course enrollment utilization rates. Compute per-building average occupancy by time of day.
- Write results back to HDFS in Parquet format

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- The most natural streaming sources in this scenario are **LMS login events**, **building access card swipes**, and **library check-ins** --- all of which arrive continuously throughout the day
- Design a Kafka topic for campus facility events (building_id, room_id, timestamp, occupancy_count)
- Use Spark Structured Streaming to maintain a running occupancy count per building
- Trigger an alert when any building exceeds 90% of its total capacity

### Stage 4: Pipeline Orchestration (Airflow)

- Build a DAG that ingests raw data into HDFS, runs Spark cleaning/joining/aggregation jobs, and produces final analytical outputs
- Include a data quality gate after ingestion (e.g., verify record counts, check for null primary keys)
- Consider separate DAG tasks for each major transformation (student profiles, course analytics, facility analytics)
- Schedule the batch pipeline for nightly execution; the streaming pipeline runs continuously

## Evaluation Focus

A strong CampusIQ submission will demonstrate:

- **Meaningful joins** across the five data sources --- the richness of this scenario comes from linking student behavior to outcomes to finances
- **Business-relevant aggregations** that directly answer the provost's questions, not just technical exercises
- **A clear retention risk model or scoring approach** --- even a simple rule-based system using engagement and GPA thresholds shows analytical thinking
- **Thoughtful HDFS zone design** that separates raw, cleaned, and analytical layers
- **A streaming prototype** that shows real-time facility monitoring is feasible
- **Well-structured Airflow DAG** with meaningful task dependencies and at least one quality gate

## Data Access

Download the datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/06-campusiq-university
```

Each team member should clone or download the data and place it in their project's `data/` directory before beginning pipeline development.
