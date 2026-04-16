#!/usr/bin/env python3
"""
Generate datasets for Project 04: MediStream Telehealth
Target: ~150-200 MB total across all files
Seed base: 2031
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta

SEED_BASE = 2031
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

NUM_PATIENTS = 50000
PATIENT_IDS = [f"PAT-{i:06d}" for i in range(1, NUM_PATIENTS + 1)]
NUM_PHYSICIANS = 800
PHYSICIAN_IDS = [f"DR-{i:04d}" for i in range(1, NUM_PHYSICIANS + 1)]

SPECIALTIES = [
    "primary_care", "dermatology", "psychiatry", "cardiology", "endocrinology",
    "orthopedics", "neurology", "gastroenterology", "pulmonology", "allergy",
    "urology", "rheumatology", "ophthalmology", "ent", "oncology"
]
SPECIALTY_WEIGHTS = [0.25, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04,
                     0.03, 0.03, 0.03, 0.03, 0.02]

# Assign physicians to specialties
rng_setup = random.Random(SEED_BASE)
PHYSICIAN_SPECIALTY = {}
for pid in PHYSICIAN_IDS:
    PHYSICIAN_SPECIALTY[pid] = rng_setup.choices(SPECIALTIES, weights=SPECIALTY_WEIGHTS, k=1)[0]

STATUSES = ["completed", "cancelled", "no_show"]
STATUS_WEIGHTS = [0.72, 0.10, 0.18]
VISIT_TYPES = ["initial", "followup", "urgent"]
VISIT_TYPE_WEIGHTS = [0.25, 0.55, 0.20]

MEASUREMENT_TYPES = ["blood_pressure", "heart_rate", "temperature", "weight", "blood_glucose"]
MEASUREMENT_WEIGHTS = [0.30, 0.25, 0.15, 0.15, 0.15]
DEVICE_TYPES_VITALS = ["manual", "wearable", "clinic"]
DEVICE_TYPE_VITALS_WEIGHTS = [0.30, 0.50, 0.20]

VIDEO_RESOLUTIONS = ["240p", "480p", "720p", "1080p"]
VIDEO_RES_WEIGHTS = [0.05, 0.15, 0.45, 0.35]
DEVICE_TYPES_SESSION = ["phone", "tablet", "laptop"]
DEVICE_TYPE_SESSION_WEIGHTS = [0.35, 0.20, 0.45]
OS_TYPES = ["iOS", "Android", "Windows", "macOS", "ChromeOS"]
OS_WEIGHTS = [0.25, 0.20, 0.25, 0.22, 0.08]

FEEDBACK_CATEGORIES = ["wait_time", "physician_manner", "technical_issues", "prescription_clarity"]


def generate_appointments():
    """Generate appointments.csv — 400K records, ~60MB"""
    rng = random.Random(SEED_BASE + 1)
    filepath = os.path.join(OUTPUT_DIR, "appointments.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2024, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["appointment_id", "patient_id", "physician_id", "scheduled_time",
                          "actual_start", "actual_end", "specialty", "status",
                          "wait_time_min", "visit_type"])
        for i in range(550000):
            appt_id = f"APPT-{i + 1:07d}"
            patient = rng.choice(PATIENT_IDS)
            physician = rng.choice(PHYSICIAN_IDS)
            specialty = PHYSICIAN_SPECIALTY[physician]

            scheduled = start_date + timedelta(minutes=rng.randint(0, 365 * 24 * 60))
            # Only schedule during business hours roughly
            scheduled = scheduled.replace(hour=rng.randint(7, 20), minute=rng.choice([0, 15, 30, 45]))

            status = rng.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
            visit_type = rng.choices(VISIT_TYPES, weights=VISIT_TYPE_WEIGHTS, k=1)[0]

            if status == "completed":
                wait = rng.randint(0, 25)
                actual_start = scheduled + timedelta(minutes=wait)
                # Duration varies by specialty
                if specialty in ("psychiatry", "oncology"):
                    duration = rng.randint(30, 60)
                elif specialty == "primary_care":
                    duration = rng.randint(10, 30)
                else:
                    duration = rng.randint(10, 45)
                actual_end = actual_start + timedelta(minutes=duration)
                actual_start_str = actual_start.strftime("%Y-%m-%d %H:%M:%S")
                actual_end_str = actual_end.strftime("%Y-%m-%d %H:%M:%S")
            else:
                wait = ""
                actual_start_str = ""
                actual_end_str = ""

            writer.writerow([
                appt_id, patient, physician,
                scheduled.strftime("%Y-%m-%d %H:%M:%S"),
                actual_start_str, actual_end_str,
                specialty, status, wait, visit_type
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_patient_vitals():
    """Generate patient-vitals.json — 300K records, ~55MB"""
    rng = random.Random(SEED_BASE + 2)
    filepath = os.path.join(OUTPUT_DIR, "patient-vitals.json")
    print(f"Generating {filepath}...")

    start_date = datetime(2024, 1, 1)
    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(400000):
            patient = rng.choice(PATIENT_IDS)
            ts = start_date + timedelta(minutes=rng.randint(0, 365 * 24 * 60))
            mtype = rng.choices(MEASUREMENT_TYPES, weights=MEASUREMENT_WEIGHTS, k=1)[0]
            device = rng.choices(DEVICE_TYPES_VITALS, weights=DEVICE_TYPE_VITALS_WEIGHTS, k=1)[0]

            if mtype == "blood_pressure":
                systolic = rng.randint(90, 180)
                diastolic = rng.randint(55, 110)
                record = {
                    "patient_id": patient,
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "measurement_type": mtype,
                    "reading": {
                        "systolic": systolic,
                        "diastolic": diastolic
                    },
                    "unit": "mmHg",
                    "device_type": device
                }
            elif mtype == "heart_rate":
                value = rng.randint(50, 120)
                record = {
                    "patient_id": patient,
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "measurement_type": mtype,
                    "value": value,
                    "unit": "bpm",
                    "device_type": device
                }
            elif mtype == "temperature":
                value = round(rng.uniform(96.0, 103.0), 1)
                record = {
                    "patient_id": patient,
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "measurement_type": mtype,
                    "value": value,
                    "unit": "fahrenheit",
                    "device_type": device
                }
            elif mtype == "weight":
                value = round(rng.uniform(100, 350), 1)
                record = {
                    "patient_id": patient,
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "measurement_type": mtype,
                    "value": value,
                    "unit": "lbs",
                    "device_type": device
                }
            else:  # blood_glucose
                value = rng.randint(60, 300)
                record = {
                    "patient_id": patient,
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "measurement_type": mtype,
                    "value": value,
                    "unit": "mg/dL",
                    "device_type": device
                }

            line = json.dumps(record)
            if i < 399999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_session_quality():
    """Generate session-quality.csv — 250K records, ~35MB"""
    rng = random.Random(SEED_BASE + 3)
    filepath = os.path.join(OUTPUT_DIR, "session-quality.csv")
    print(f"Generating {filepath}...")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["session_id", "appointment_id", "video_resolution",
                          "audio_quality_score", "latency_ms", "packet_loss_pct",
                          "duration_sec", "device_type", "os"])
        for i in range(250000):
            sess_id = f"SESS-{i + 1:07d}"
            appt_id = f"APPT-{i + 1:07d}"  # 1:1 with completed appointments

            resolution = rng.choices(VIDEO_RESOLUTIONS, weights=VIDEO_RES_WEIGHTS, k=1)[0]
            device = rng.choices(DEVICE_TYPES_SESSION, weights=DEVICE_TYPE_SESSION_WEIGHTS, k=1)[0]
            os_type = rng.choices(OS_TYPES, weights=OS_WEIGHTS, k=1)[0]

            # Quality metrics — phone tends to be worse
            if device == "phone":
                latency = round(rng.uniform(30, 800), 1)
                packet_loss = round(rng.uniform(0, 8), 2)
                audio = rng.randint(4, 10)
            elif device == "tablet":
                latency = round(rng.uniform(20, 500), 1)
                packet_loss = round(rng.uniform(0, 5), 2)
                audio = rng.randint(5, 10)
            else:  # laptop
                latency = round(rng.uniform(10, 300), 1)
                packet_loss = round(rng.uniform(0, 3), 2)
                audio = rng.randint(6, 10)

            duration = rng.randint(300, 3600)  # 5 min to 60 min

            writer.writerow([
                sess_id, appt_id, resolution, audio, latency,
                packet_loss, duration, device, os_type
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_patient_feedback():
    """Generate patient-feedback.json — 50K records, ~10MB"""
    rng = random.Random(SEED_BASE + 4)
    filepath = os.path.join(OUTPUT_DIR, "patient-feedback.json")
    print(f"Generating {filepath}...")

    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(50000):
            fb_id = f"FB-{i + 1:06d}"
            # Feedback comes from completed appointments
            appt_id = f"APPT-{rng.randint(1, 300000):07d}"
            patient = rng.choice(PATIENT_IDS)

            rating = rng.choices([1, 2, 3, 4, 5],
                                  weights=[0.05, 0.08, 0.15, 0.35, 0.37], k=1)[0]

            # Categories mentioned — more complaints when low rating
            num_cats = rng.randint(1, 3) if rating <= 3 else rng.randint(0, 2)
            cats = rng.sample(FEEDBACK_CATEGORIES, k=min(num_cats, len(FEEDBACK_CATEGORIES)))

            # NPS: correlated with rating
            if rating >= 4:
                nps = rng.randint(7, 10)
            elif rating == 3:
                nps = rng.randint(4, 7)
            else:
                nps = rng.randint(0, 5)

            record = {
                "feedback_id": fb_id,
                "appointment_id": appt_id,
                "patient_id": patient,
                "rating": rating,
                "categories_mentioned": cats,
                "nps_score": nps
            }
            line = json.dumps(record)
            if i < 49999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_physician_schedule():
    """Generate physician-schedule.csv — 30K records, ~4MB"""
    rng = random.Random(SEED_BASE + 5)
    filepath = os.path.join(OUTPUT_DIR, "physician-schedule.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2024, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["physician_id", "date", "start_time", "end_time",
                          "specialty", "max_appointments", "actual_appointments"])
        for i in range(30000):
            physician = rng.choice(PHYSICIAN_IDS)
            date = start_date + timedelta(days=rng.randint(0, 365))
            specialty = PHYSICIAN_SPECIALTY[physician]

            start_hour = rng.choice([7, 8, 9])
            end_hour = rng.choice([16, 17, 18, 19, 20])
            start_time = f"{start_hour:02d}:00"
            end_time = f"{end_hour:02d}:00"

            hours_available = end_hour - start_hour
            if specialty in ("psychiatry", "oncology"):
                max_appts = hours_available  # ~1 per hour (longer sessions)
            else:
                max_appts = int(hours_available * rng.uniform(1.5, 3.0))

            # Utilization varies
            utilization = rng.uniform(0.4, 1.0)
            actual = min(max_appts, max(1, int(max_appts * utilization)))

            writer.writerow([
                physician, date.strftime("%Y-%m-%d"),
                start_time, end_time, specialty,
                max_appts, actual
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


if __name__ == "__main__":
    print("=" * 60)
    print("Project 04: MediStream Telehealth — Data Generation")
    print("=" * 60)
    generate_appointments()
    generate_patient_vitals()
    generate_session_quality()
    generate_patient_feedback()
    generate_physician_schedule()
    print("\nAll files generated successfully!")
    total = sum(
        os.path.getsize(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith((".csv", ".json"))
    )
    print(f"Total size: {total / 1e6:.1f} MB")
