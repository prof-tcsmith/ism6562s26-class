#!/usr/bin/env python3
"""
Generate synthetic datasets for CampusIQ University (Project 06).
Seed base: 2051. Target total: ~165 MB.

Usage: python3 generate_data.py
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_BASE = 2051


# ---------------------------------------------------------------------------
# Shared reference data
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    "Computer Science", "Mathematics", "Biology", "Chemistry", "Physics",
    "Psychology", "English", "History", "Business Administration", "Finance",
    "Marketing", "Accounting", "Economics", "Political Science", "Sociology",
    "Nursing", "Engineering", "Art", "Music", "Philosophy",
    "Communication", "Education", "Public Health", "Statistics",
    "Information Systems", "Environmental Science", "Criminal Justice",
    "Architecture", "Theater", "Anthropology"
]

MAJORS = DEPARTMENTS[:20]  # Top 20 departments as majors

BUILDINGS = [f"BLD-{i:03d}" for i in range(1, 51)]

ROOM_TYPES = ["classroom", "lab", "library", "dining", "gym"]

SEMESTERS = ["2023-Fall", "2024-Spring", "2024-Fall", "2025-Spring",
             "2025-Fall", "2026-Spring"]

SCHOLARSHIP_TYPES = ["merit", "need_based", "athletic", "departmental",
                     "external", "none"]

ENGAGEMENT_EVENTS = ["lms_login", "library_visit", "tutoring",
                     "office_hours", "club_meeting", "dining"]

PLATFORMS = ["web", "mobile", "in_person"]

GRADES = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]
GRADE_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0
}


FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William",
    "Linda", "David", "Elizabeth", "Richard", "Barbara", "Joseph", "Susan",
    "Thomas", "Jessica", "Charles", "Sarah", "Christopher", "Karen",
    "Daniel", "Lisa", "Matthew", "Nancy", "Anthony", "Betty", "Mark",
    "Margaret", "Donald", "Sandra", "Steven", "Ashley", "Paul", "Kimberly",
    "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson"
]


def generate_course_ids():
    """Pre-generate a pool of course IDs."""
    rng = random.Random(SEED_BASE + 100)
    course_ids = []
    for dept in DEPARTMENTS:
        prefix = dept[:3].upper()
        for level in [1, 2, 3, 4, 5]:
            for seq in range(1, 21):
                course_ids.append(f"{prefix}{level}{seq:02d}")
    return course_ids


COURSE_IDS = generate_course_ids()


# ---------------------------------------------------------------------------
# 1. student-records.csv  (~60 MB, 400K records)
# ---------------------------------------------------------------------------

def generate_student_records():
    rng = random.Random(SEED_BASE + 1)
    outpath = os.path.join(SCRIPT_DIR, "student-records.csv")

    student_ids = [f"STU-{i:06d}" for i in range(1, 30001)]
    num_records = 750_000

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "student_id", "semester", "course_id", "grade", "credit_hours",
            "gpa_semester", "gpa_cumulative", "major", "class_standing",
            "enrollment_status", "financial_aid"
        ])

        standings = ["freshman", "sophomore", "junior", "senior"]

        for _ in range(num_records):
            sid = rng.choice(student_ids)
            semester = rng.choice(SEMESTERS)
            course_id = rng.choice(COURSE_IDS[:300])
            grade = rng.choices(
                GRADES,
                weights=[15, 10, 12, 18, 10, 8, 10, 5, 4, 3, 5],
                k=1
            )[0]
            credit_hours = rng.choice([1, 2, 3, 3, 3, 4, 4])
            gpa_sem = round(rng.gauss(3.0, 0.6), 2)
            gpa_sem = max(0.0, min(4.0, gpa_sem))
            gpa_cum = round(rng.gauss(2.9, 0.5), 2)
            gpa_cum = max(0.0, min(4.0, gpa_cum))
            major = rng.choice(MAJORS)
            standing = rng.choice(standings)
            enroll = rng.choices(
                ["full_time", "part_time"], weights=[80, 20], k=1
            )[0]
            fin_aid = rng.choices([True, False], weights=[65, 35], k=1)[0]

            writer.writerow([
                sid, semester, course_id, grade, credit_hours,
                f"{gpa_sem:.2f}", f"{gpa_cum:.2f}", major, standing,
                enroll, fin_aid
            ])

    print(f"  student-records.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 2. course-catalog.json  (~10 MB, 50K records)
# ---------------------------------------------------------------------------

def generate_course_catalog():
    rng = random.Random(SEED_BASE + 2)
    outpath = os.path.join(SCRIPT_DIR, "course-catalog.json")

    num_records = 50_000
    day_times = [
        "MWF 08:00-08:50", "MWF 09:00-09:50", "MWF 10:00-10:50",
        "MWF 11:00-11:50", "MWF 12:00-12:50", "MWF 13:00-13:50",
        "MWF 14:00-14:50", "TR 08:00-09:15", "TR 09:30-10:45",
        "TR 11:00-12:15", "TR 12:30-13:45", "TR 14:00-15:15",
        "TR 15:30-16:45", "MW 18:00-19:15", "TR 18:00-19:15",
        "Online Async", "Online Sync MW 19:00-20:15"
    ]

    instructor_ids = [f"FAC-{i:04d}" for i in range(1, 3001)]

    records = []
    for _ in range(num_records):
        dept = rng.choice(DEPARTMENTS)
        prefix = dept[:3].upper()
        level = rng.choice([1, 2, 3, 4, 5])
        seq = rng.randint(1, 20)
        cid = f"{prefix}{level}{seq:02d}"
        capacity = rng.choice([25, 30, 35, 40, 50, 60, 80, 100, 150, 200])
        enrolled = rng.randint(max(5, int(capacity * 0.3)), capacity)
        waitlist = rng.randint(0, 30) if enrolled >= capacity * 0.9 else 0
        building = rng.choice(BUILDINGS)
        room = f"{building}-{rng.randint(100, 499)}"

        course_name_adj = rng.choice([
            "Introduction to", "Advanced", "Principles of", "Topics in",
            "Seminar in", "Applied", "Foundations of", "Research Methods in"
        ])

        records.append({
            "course_id": cid,
            "department": dept,
            "course_name": f"{course_name_adj} {dept} {level}00-level",
            "credits": rng.choice([1, 2, 3, 3, 3, 4, 4]),
            "capacity": capacity,
            "instructor_id": rng.choice(instructor_ids),
            "semester": rng.choice(SEMESTERS),
            "day_time": rng.choice(day_times),
            "room": room,
            "enrolled_count": enrolled,
            "waitlist_count": waitlist
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  course-catalog.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 3. campus-facilities.csv  (~30 MB, 200K records)
# ---------------------------------------------------------------------------

def generate_campus_facilities():
    rng = random.Random(SEED_BASE + 3)
    outpath = os.path.join(SCRIPT_DIR, "campus-facilities.csv")

    num_records = 400_000
    rooms_per_building = {}
    for bld in BUILDINGS:
        n_rooms = rng.randint(10, 50)
        rooms_per_building[bld] = [
            (f"{bld}-{rng.randint(100, 499)}", rng.choice(ROOM_TYPES),
             rng.randint(20, 300))
            for _ in range(n_rooms)
        ]

    base_date = datetime(2025, 1, 1)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "building_id", "room_id", "timestamp", "occupancy_count",
            "capacity", "type", "hvac_kwh", "lighting_kwh"
        ])

        for _ in range(num_records):
            bld = rng.choice(BUILDINGS)
            room_id, rtype, capacity = rng.choice(rooms_per_building[bld])
            ts = base_date + timedelta(
                days=rng.randint(0, 180),
                hours=rng.randint(6, 23),
                minutes=rng.choice([0, 15, 30, 45])
            )
            # Occupancy depends on time of day
            hour = ts.hour
            if 8 <= hour <= 17:
                occ_pct = rng.gauss(0.55, 0.25)
            elif 18 <= hour <= 21:
                occ_pct = rng.gauss(0.25, 0.15)
            else:
                occ_pct = rng.gauss(0.05, 0.03)
            occ_pct = max(0.0, min(1.0, occ_pct))
            occupancy = int(capacity * occ_pct)

            hvac = round(rng.uniform(0.5, 15.0) * (0.3 + occ_pct), 2)
            lighting = round(rng.uniform(0.2, 5.0) * (0.2 + occ_pct * 0.8), 2)

            writer.writerow([
                bld, room_id, ts.strftime("%Y-%m-%d %H:%M:%S"),
                occupancy, capacity, rtype,
                f"{hvac:.2f}", f"{lighting:.2f}"
            ])

    print(f"  campus-facilities.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 4. student-engagement.json  (~50 MB, 300K records)
# ---------------------------------------------------------------------------

def generate_student_engagement():
    rng = random.Random(SEED_BASE + 4)
    outpath = os.path.join(SCRIPT_DIR, "student-engagement.json")

    num_records = 550_000
    student_ids = [f"STU-{i:06d}" for i in range(1, 30001)]
    base_date = datetime(2025, 1, 6)

    records = []
    for _ in range(num_records):
        sid = rng.choice(student_ids)
        ts = base_date + timedelta(
            days=rng.randint(0, 150),
            hours=rng.randint(6, 23),
            minutes=rng.randint(0, 59),
            seconds=rng.randint(0, 59)
        )
        event = rng.choices(
            ENGAGEMENT_EVENTS,
            weights=[35, 15, 10, 8, 12, 20],
            k=1
        )[0]

        if event == "lms_login":
            duration = rng.randint(2, 120)
            platform = rng.choices(["web", "mobile"], weights=[60, 40], k=1)[0]
        elif event == "library_visit":
            duration = rng.randint(15, 300)
            platform = "in_person"
        elif event == "tutoring":
            duration = rng.randint(20, 90)
            platform = rng.choices(
                ["in_person", "web"], weights=[70, 30], k=1
            )[0]
        elif event == "office_hours":
            duration = rng.randint(10, 60)
            platform = rng.choices(
                ["in_person", "web"], weights=[60, 40], k=1
            )[0]
        elif event == "club_meeting":
            duration = rng.randint(30, 120)
            platform = "in_person"
        else:  # dining
            duration = rng.randint(10, 60)
            platform = "in_person"

        records.append({
            "student_id": sid,
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
            "event_type": event,
            "duration_minutes": duration,
            "platform": platform
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  student-engagement.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 5. financial-data.csv  (~15 MB, 100K records)
# ---------------------------------------------------------------------------

def generate_financial_data():
    rng = random.Random(SEED_BASE + 5)
    outpath = os.path.join(SCRIPT_DIR, "financial-data.csv")

    num_records = 200_000
    student_ids = [f"STU-{i:06d}" for i in range(1, 30001)]

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "student_id", "semester", "tuition_charged", "tuition_paid",
            "financial_aid_amount", "outstanding_balance", "payment_plan",
            "scholarship_type"
        ])

        for _ in range(num_records):
            sid = rng.choice(student_ids)
            semester = rng.choice(SEMESTERS)

            tuition = round(rng.gauss(8500, 2000), 2)
            tuition = max(2000, min(20000, tuition))

            scholarship = rng.choices(
                SCHOLARSHIP_TYPES,
                weights=[15, 25, 5, 10, 10, 35],
                k=1
            )[0]

            if scholarship == "none":
                aid = 0.0
            elif scholarship == "athletic":
                aid = round(tuition * rng.uniform(0.5, 1.0), 2)
            elif scholarship == "merit":
                aid = round(tuition * rng.uniform(0.2, 0.6), 2)
            elif scholarship == "need_based":
                aid = round(tuition * rng.uniform(0.3, 0.8), 2)
            else:
                aid = round(tuition * rng.uniform(0.1, 0.4), 2)

            paid = round(rng.uniform(0.5, 1.0) * (tuition - aid), 2)
            paid = max(0, paid)
            balance = round(tuition - aid - paid, 2)
            balance = max(0, balance)
            payment_plan = balance > 500 and rng.random() < 0.6

            writer.writerow([
                sid, semester, f"{tuition:.2f}", f"{paid:.2f}",
                f"{aid:.2f}", f"{balance:.2f}", payment_plan, scholarship
            ])

    print(f"  financial-data.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating CampusIQ University datasets (seed base=2051)...")
    generate_student_records()
    generate_course_catalog()
    generate_campus_facilities()
    generate_student_engagement()
    generate_financial_data()
    print("Done.")
