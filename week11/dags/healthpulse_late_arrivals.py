"""
ISM 6562 — Week 11: HealthPulse Late-Arrival Sensor Pipeline
=============================================================
Demonstrates the Airflow **sensor** operator family — tasks that wait for
something to happen before the DAG proceeds. This is the third core
operator family alongside BashOperator and PythonOperator.

Scenario:
  HealthPulse's hospital partners drop patient-feed CSV files into a
  landing zone on unpredictable schedules (usually by 06:00, sometimes
  late). This DAG runs daily, waits up to 2 hours for the day's file to
  arrive, and then processes it. If the file never arrives within the
  window, the DAG fails fast so the on-call engineer is alerted.

Sensor operators used:
  - FileSensor: polls for the existence of a file on a filesystem path,
    succeeds when the file appears.

Pipeline structure:

  wait_for_daily_feed   (FileSensor: waits up to 2h for /opt/airflow/data/...{ds}.csv)
        |
    validate_file        (PythonOperator: checks size/row-count sanity)
        |
    process_late_arrival (BashOperator: simulates downstream processing)
        |
    notify_on_call       (PythonOperator: emits a note about when the file landed)

Why students should care:
  - Sensors let a DAG **block** waiting for an external condition without
    the team writing their own polling loop.
  - Sensors use retry/timeout semantics that are distinct from task retries —
    students often confuse the two.
  - Choosing a sensor's poke_interval and timeout is a real engineering
    trade-off: too fast = wasted scheduler cycles, too slow = stale alerts.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

# -------------------------------------------------------------------------
# Default arguments
# -------------------------------------------------------------------------
default_args = {
    "owner": "healthpulse-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=3),
}


# -------------------------------------------------------------------------
# Python callables
# -------------------------------------------------------------------------

def validate_patient_file(**context):
    """
    Sanity-check the file the sensor just found. In production this would
    open the CSV and check row counts, schema, and checksum; for the lab we
    just emit a size-and-arrival-time record.
    """
    import os
    ds = context["ds"]
    path = f"/opt/airflow/data/healthpulse/daily-patient-feed/{ds}.csv"

    if not os.path.exists(path):
        # Shouldn't happen — sensor upstream should have caught this.
        raise FileNotFoundError(f"File disappeared between sensor and validation: {path}")

    size_bytes = os.path.getsize(path)
    print(f"Validating {path}")
    print(f"  size:      {size_bytes:,} bytes")
    print(f"  landed at: {datetime.utcnow().isoformat()}Z")

    if size_bytes < 100:
        raise ValueError(
            f"File {path} is suspiciously small ({size_bytes} bytes) — "
            f"downstream refusing to process"
        )

    context["ti"].xcom_push(key="file_size_bytes", value=size_bytes)
    context["ti"].xcom_push(key="file_path", value=path)


def notify_pipeline_complete(**context):
    """
    Simulate an on-call notification with the arrival lag expressed in minutes.
    """
    ti = context["ti"]
    size = ti.xcom_pull(task_ids="validate_file", key="file_size_bytes")
    path = ti.xcom_pull(task_ids="validate_file", key="file_path")

    print(f"Late-arrival pipeline completed for {context['ds']}")
    print(f"  file:  {path}")
    print(f"  size:  {size:,} bytes")
    print("  Notification sent to #healthpulse-data-ops Slack channel.")


# -------------------------------------------------------------------------
# DAG definition
# -------------------------------------------------------------------------

with DAG(
    dag_id="healthpulse_late_arrivals",
    default_args=default_args,
    description="Wait for daily patient feed to land, then process it",
    schedule="0 6 * * *",         # Daily at 06:00 UTC (the arrival window opens)
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["healthpulse", "daily", "sensor", "pipeline"],
) as dag:

    # --- Task 1: Wait for the daily feed file to arrive ---
    #
    # FileSensor pokes every 60 seconds, times out after 2 hours. Without
    # this sensor, students would have to build their own retry loop; with
    # it, Airflow handles the polling and correctly records WAITING time
    # separate from task runtime.
    #
    # mode="reschedule" (rather than the default "poke") frees up the worker
    # slot between pokes — important for long-waiting sensors so they don't
    # block the worker pool.
    wait_for_file = FileSensor(
        task_id="wait_for_daily_feed",
        filepath="/opt/airflow/data/healthpulse/daily-patient-feed/{{ ds }}.csv",
        poke_interval=60,                       # check every 60 seconds
        timeout=60 * 60 * 2,                    # give up after 2 hours
        mode="reschedule",                      # free worker slot between pokes
        soft_fail=False,                        # timeout = DAG failure (alertable)
    )

    # --- Task 2: Validate the file that just arrived ---
    validate = PythonOperator(
        task_id="validate_file",
        python_callable=validate_patient_file,
    )

    # --- Task 3: Simulate downstream processing ---
    process = BashOperator(
        task_id="process_late_arrival",
        bash_command=(
            'echo "Processing late-arrival file for {{ ds }}..." && '
            'echo "  - Upsert into patient_facts (partitioned by dt={{ ds }})" && '
            'echo "  - Refresh materialized view: daily_patient_summary" && '
            'echo "Processing complete."'
        ),
    )

    # --- Task 4: Notify on-call that the late-arrival flow finished ---
    notify = PythonOperator(
        task_id="notify_on_call",
        python_callable=notify_pipeline_complete,
    )

    # Linear pipeline: sensor blocks until file lands, then we process.
    wait_for_file >> validate >> process >> notify
