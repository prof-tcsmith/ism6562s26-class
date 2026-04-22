"""
ISM 6562 — Week 11: GreenRoute Weekly Fleet Report
====================================================
Demonstrates Airflow orchestrating a Spark-based analytics pipeline:
  - Weekly schedule (Monday at 2:00 AM)
  - Spark job simulation via BashOperator
  - GPS data quality checks (lat/lon range validation)
  - Multi-step pipeline with clear task separation
  - Notification on completion

Pipeline structure:

  validate_gps_data → aggregate_fleet_metrics → generate_report → notify
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# -------------------------------------------------------------------------
# Default arguments
# -------------------------------------------------------------------------
default_args = {
    "owner": "greenroute-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=10),
    "execution_timeout": timedelta(hours=1),
}


# -------------------------------------------------------------------------
# Python callables
# -------------------------------------------------------------------------

def validate_gps_quality(**context):
    """
    Validate GPS data quality for the reporting week.
    Checks:
      - Latitude must be in [-90, 90]
      - Longitude must be in [-180, 180]
      - Coordinates of (0, 0) are flagged as missing/default
      - Speed must be non-negative
    """
    import random
    random.seed(2026)

    total_records = 1000
    impossible_coords = 0
    null_island = 0       # (0, 0) coordinates — common GPS default error
    negative_speeds = 0

    for _ in range(total_records):
        lat = random.uniform(-95, 95)
        lon = random.uniform(-185, 185)
        speed = random.uniform(-5, 80)

        if abs(lat) > 90 or abs(lon) > 180:
            impossible_coords += 1
        if lat == 0.0 and lon == 0.0:
            null_island += 1
        if speed < 0:
            negative_speeds += 1

    total_issues = impossible_coords + null_island + negative_speeds
    issue_rate = total_issues / total_records

    print(f"GPS Quality Check for week of {context['ds']}:")
    print(f"  Total records:       {total_records}")
    print(f"  Impossible coords:   {impossible_coords}")
    print(f"  Null Island (0,0):   {null_island}")
    print(f"  Negative speeds:     {negative_speeds}")
    print(f"  Issue rate:          {issue_rate:.2%}")

    context["ti"].xcom_push(key="total_records", value=total_records)
    context["ti"].xcom_push(key="issues_found", value=total_issues)
    context["ti"].xcom_push(key="clean_records", value=total_records - total_issues)

    if issue_rate > 0.20:
        raise ValueError(
            f"GPS quality check FAILED: {issue_rate:.2%} issue rate exceeds 20% threshold"
        )

    print(f"GPS quality check PASSED. {total_records - total_issues} clean records.")


def send_report_notification(**context):
    """
    Simulate sending the weekly fleet report notification.
    """
    ti = context["ti"]
    clean = ti.xcom_pull(task_ids="validate_gps_data", key="clean_records")
    print(f"Weekly fleet report for {context['ds']} is ready.")
    print(f"  Clean GPS records used: {clean}")
    print("Report published to /reports/fleet-weekly/")
    print("Notification sent to #greenroute-ops channel.")


# -------------------------------------------------------------------------
# DAG definition
# -------------------------------------------------------------------------

with DAG(
    dag_id="greenroute_weekly_report",
    default_args=default_args,
    description="Weekly fleet metrics aggregation and reporting via Spark",
    schedule="0 2 * * MON",     # Every Monday at 2:00 AM
    # Backdated so students can trigger task runs immediately during lab.
    # catchup=False prevents Airflow from creating historical runs.
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["greenroute", "weekly", "spark", "fleet"],
) as dag:

    # --- Task 1: Validate GPS data quality ---
    validate_gps = PythonOperator(
        task_id="validate_gps_data",
        python_callable=validate_gps_quality,
    )

    # --- Task 2: Aggregate fleet metrics via Spark ---
    # In production, this would run: spark-submit --master spark://spark-master:7077
    # For the lab, we simulate the Spark job output.
    aggregate = BashOperator(
        task_id="aggregate_fleet_metrics",
        bash_command=(
            'echo "Submitting Spark job to spark://spark-master:7077..." && '
            'echo "spark-submit --master spark://spark-master:7077 '
            '/opt/airflow/dags/jobs/fleet_aggregation.py" && '
            'echo "" && '
            'echo "Spark Job Output:" && '
            'echo "  - Reading GPS data for week {{ ds }}" && '
            'echo "  - Computing total_miles, total_hours, avg_speed per truck" && '
            'echo "  - Computing idle_hours (speed < 2 mph)" && '
            'echo "  - Computing fuel efficiency (miles / gallons)" && '
            'echo "  - Writing results to /data/fleet-weekly/{{ ds }}.parquet" && '
            'echo "Spark job completed successfully."'
        ),
    )

    # --- Task 3: Generate fleet report ---
    generate_report = BashOperator(
        task_id="generate_report",
        bash_command=(
            'echo "Generating weekly fleet report for {{ ds }}..." && '
            'echo "  - Top 5 trucks by total miles" && '
            'echo "  - Bottom 5 trucks by fuel efficiency" && '
            'echo "  - Fleet-wide idle hours summary" && '
            'echo "  - Week-over-week trend comparison" && '
            'echo "Report saved to /reports/fleet-weekly/{{ ds }}.html"'
        ),
    )

    # --- Task 4: Send notification ---
    notify = PythonOperator(
        task_id="send_notification",
        python_callable=send_report_notification,
    )

    # --- Dependencies: linear chain ---
    validate_gps >> aggregate >> generate_report >> notify
