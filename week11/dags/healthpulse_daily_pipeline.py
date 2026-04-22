"""
ISM 6562 — Week 11: HealthPulse Daily Patient Pipeline
=======================================================
Demonstrates core Airflow concepts:
  - Scheduled DAG (daily at 2:00 AM)
  - BashOperator and PythonOperator tasks
  - Task dependencies (linear chain + diamond pattern)
  - Data quality checks with Python callables
  - Retry and timeout configuration
  - XCom for passing values between tasks

Pipeline structure (diamond dependency):

  ingest_patient_feed
         |
    validate_data
       /    \
  transform   quality_report
       \    /
    load_to_warehouse
         |
    send_notification
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# -------------------------------------------------------------------------
# Default arguments applied to every task in the DAG
# -------------------------------------------------------------------------
default_args = {
    "owner": "healthpulse-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}


# -------------------------------------------------------------------------
# Python callables used by PythonOperator tasks
# -------------------------------------------------------------------------

def validate_patient_data(**context):
    """
    Simulate a data quality gate on the daily patient feed.
    In production this would read from a staging table or file and check
    for nulls, schema drift, and referential integrity.
    """
    import random
    random.seed(42)

    total_records = 5000
    null_patient_ids = random.randint(0, 50)
    negative_costs = random.randint(0, 25)
    future_dates = random.randint(0, 15)

    errors = null_patient_ids + negative_costs + future_dates
    error_rate = errors / total_records

    print(f"Validation results for {context['ds']}:")
    print(f"  Total records:     {total_records}")
    print(f"  Null patient_ids:  {null_patient_ids}")
    print(f"  Negative costs:    {negative_costs}")
    print(f"  Future dates:      {future_dates}")
    print(f"  Error rate:        {error_rate:.2%}")

    # Push metrics to XCom so downstream tasks can access them
    context["ti"].xcom_push(key="total_records", value=total_records)
    context["ti"].xcom_push(key="error_count", value=errors)
    context["ti"].xcom_push(key="error_rate", value=round(error_rate, 4))

    # Fail the task if error rate exceeds threshold
    if error_rate > 0.05:
        raise ValueError(
            f"Data quality check FAILED: error rate {error_rate:.2%} "
            f"exceeds 5% threshold"
        )

    print("Data quality check PASSED.")


def generate_quality_report(**context):
    """
    Generate a summary quality report. Pulls validation metrics from XCom.
    In production this would write to a monitoring dashboard or S3.
    """
    ti = context["ti"]
    total = ti.xcom_pull(task_ids="validate_data", key="total_records")
    errors = ti.xcom_pull(task_ids="validate_data", key="error_count")
    rate = ti.xcom_pull(task_ids="validate_data", key="error_rate")

    report = (
        f"=== HealthPulse Daily Quality Report ({context['ds']}) ===\n"
        f"Records processed: {total}\n"
        f"Records with issues: {errors}\n"
        f"Error rate: {rate}\n"
        f"Status: {'PASS' if rate <= 0.05 else 'FAIL'}\n"
    )
    print(report)


def send_pipeline_notification(**context):
    """
    Simulate sending a notification (Slack, email, etc.) on pipeline completion.
    """
    print(f"Pipeline completed successfully for {context['ds']}.")
    print("Notification sent to #healthpulse-data-ops channel.")


# -------------------------------------------------------------------------
# DAG definition
# -------------------------------------------------------------------------

with DAG(
    dag_id="healthpulse_daily_pipeline",
    default_args=default_args,
    description="Daily ingestion, validation, and loading of patient data",
    schedule="0 2 * * *",        # Every day at 2:00 AM
    # Backdated so students can trigger task runs immediately during lab.
    # catchup=False prevents Airflow from creating historical runs.
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["healthpulse", "daily", "pipeline"],
) as dag:

    # --- Task 1: Ingest the daily patient feed ---
    ingest = BashOperator(
        task_id="ingest_patient_feed",
        bash_command=(
            'echo "Ingesting patient feed for {{ ds }}..." && '
            'echo "Downloading from /data/daily-patient-feed/{{ ds }}.csv" && '
            'echo "Loaded 5000 records into staging table."'
        ),
    )

    # --- Task 2: Validate data quality ---
    validate = PythonOperator(
        task_id="validate_data",
        python_callable=validate_patient_data,
    )

    # --- Task 3a: Transform data (diamond left branch) ---
    transform = BashOperator(
        task_id="transform_data",
        bash_command=(
            'echo "Applying transformations for {{ ds }}..." && '
            'echo "  - Standardizing diagnosis codes to ICD-10" && '
            'echo "  - Computing cost quartiles per department" && '
            'echo "  - Deduplicating by patient_id + admission_date" && '
            'echo "Transformation complete: 4,850 clean records."'
        ),
    )

    # --- Task 3b: Generate quality report (diamond right branch) ---
    quality_report = PythonOperator(
        task_id="quality_report",
        python_callable=generate_quality_report,
    )

    # --- Task 4: Load to data warehouse (diamond join) ---
    load = BashOperator(
        task_id="load_to_warehouse",
        bash_command=(
            'echo "Loading transformed data into warehouse for {{ ds }}..." && '
            'echo "  - INSERT INTO warehouse.patient_facts SELECT ... FROM staging" && '
            'echo "  - Updating partition: dt={{ ds }}" && '
            'echo "Load complete."'
        ),
    )

    # --- Task 5: Send notification ---
    notify = PythonOperator(
        task_id="send_notification",
        python_callable=send_pipeline_notification,
    )

    # --- Dependencies ---
    # Linear: ingest → validate
    # Diamond: validate → [transform, quality_report] → load
    # Linear: load → notify

    ingest >> validate
    validate >> [transform, quality_report]
    [transform, quality_report] >> load
    load >> notify
