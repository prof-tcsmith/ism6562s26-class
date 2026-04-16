#!/usr/bin/env python3
"""
Generate datasets for Project 02: CityTransit Mobility (MetroLink Transit)
Target: ~150-200 MB total across all files
Seed base: 2011
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta

SEED_BASE = 2011
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Routes and infrastructure
NUM_BUSES = 450
BUS_IDS = [f"BUS-{i:03d}" for i in range(1, NUM_BUSES + 1)]
NUM_ROUTES = 62
ROUTE_IDS = [f"R-{i:02d}" for i in range(1, NUM_ROUTES + 1)]
RAIL_LINES = ["red", "blue", "green"]
NUM_RAIL_STATIONS = 45
RAIL_STATION_IDS = [f"RS-{i:02d}" for i in range(1, NUM_RAIL_STATIONS + 1)]
NUM_BIKESHARE_STATIONS = 320
BIKESHARE_STATION_IDS = [f"BS-{i:03d}" for i in range(1, NUM_BIKESHARE_STATIONS + 1)]
NUM_BIKES = 5000
BIKE_IDS = [f"BK-{i:04d}" for i in range(1, NUM_BIKES + 1)]
DAY_TYPES = ["weekday", "saturday", "sunday"]
USER_TYPES = ["subscriber", "casual"]
COMPLAINT_CATEGORIES = ["delay", "overcrowding", "safety", "cleanliness", "driver"]
COMPLAINT_CATEGORY_WEIGHTS = [0.35, 0.25, 0.10, 0.15, 0.15]
WEATHER_CONDITIONS = ["clear", "cloudy", "rain", "heavy_rain", "snow", "fog"]
WEATHER_CONDITION_WEIGHTS = [0.35, 0.25, 0.18, 0.08, 0.08, 0.06]

# Assign buses to routes
BUS_ROUTE_MAP = {bid: ROUTE_IDS[i % NUM_ROUTES] for i, bid in enumerate(BUS_IDS)}
# Assign stations to lines
STATION_LINE_MAP = {}
for i, sid in enumerate(RAIL_STATION_IDS):
    STATION_LINE_MAP[sid] = RAIL_LINES[i % 3]

# Base lat/lon for a metro area (approximate Tampa FL area)
BASE_LAT, BASE_LON = 27.95, -82.46


def generate_bus_telemetry():
    """Generate bus-telemetry.csv — 600K records, ~90MB"""
    rng = random.Random(SEED_BASE + 1)
    filepath = os.path.join(OUTPUT_DIR, "bus-telemetry.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2025, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["bus_id", "route_id", "timestamp", "lat", "lon", "speed_mph",
                          "passenger_count", "door_open_count", "fuel_level_pct"])
        for i in range(1300000):
            bus = rng.choice(BUS_IDS)
            route = BUS_ROUTE_MAP[bus]
            ts = start_date + timedelta(seconds=rng.randint(0, 180 * 24 * 3600))
            hour = ts.hour

            lat = round(BASE_LAT + rng.uniform(-0.15, 0.15), 6)
            lon = round(BASE_LON + rng.uniform(-0.20, 0.20), 6)

            # Speed varies by time of day
            if 7 <= hour <= 9 or 16 <= hour <= 18:
                speed = round(rng.uniform(5, 25), 1)  # Rush hour - slower
            elif 22 <= hour or hour <= 5:
                speed = round(rng.uniform(15, 45), 1)  # Night - faster
            else:
                speed = round(rng.uniform(10, 35), 1)

            # Passenger count varies by time
            if 7 <= hour <= 9:
                passengers = rng.randint(15, 65)
            elif 16 <= hour <= 18:
                passengers = rng.randint(20, 70)
            elif 10 <= hour <= 15:
                passengers = rng.randint(8, 40)
            else:
                passengers = rng.randint(2, 20)

            door_opens = rng.randint(0, 8)
            fuel = round(rng.uniform(10, 100), 1)

            writer.writerow([bus, route, ts.strftime("%Y-%m-%d %H:%M:%S"),
                              lat, lon, speed, passengers, door_opens, fuel])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_rail_ridership():
    """Generate rail-ridership.json — 300K records, ~50MB"""
    rng = random.Random(SEED_BASE + 2)
    filepath = os.path.join(OUTPUT_DIR, "rail-ridership.json")
    print(f"Generating {filepath}...")

    start_date = datetime(2025, 1, 1)
    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(500000):
            station = rng.choice(RAIL_STATION_IDS)
            ts = start_date + timedelta(hours=rng.randint(0, 180 * 24))
            line = STATION_LINE_MAP[station]
            dow = ts.weekday()
            if dow < 5:
                day_type = "weekday"
            elif dow == 5:
                day_type = "saturday"
            else:
                day_type = "sunday"

            hour = ts.hour
            # Ridership varies by time and day type
            if day_type == "weekday":
                if 7 <= hour <= 9:
                    entries = rng.randint(50, 400)
                    exits = rng.randint(30, 350)
                elif 16 <= hour <= 18:
                    entries = rng.randint(30, 350)
                    exits = rng.randint(50, 400)
                elif 10 <= hour <= 15:
                    entries = rng.randint(20, 150)
                    exits = rng.randint(20, 150)
                else:
                    entries = rng.randint(5, 60)
                    exits = rng.randint(5, 60)
            elif day_type == "saturday":
                if 10 <= hour <= 20:
                    entries = rng.randint(30, 200)
                    exits = rng.randint(30, 200)
                else:
                    entries = rng.randint(5, 50)
                    exits = rng.randint(5, 50)
            else:
                entries = rng.randint(5, 100)
                exits = rng.randint(5, 100)

            record = {
                "station_id": station,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "entries": entries,
                "exits": exits,
                "line": line,
                "day_type": day_type
            }
            line_str = json.dumps(record)
            if i < 499999:
                f.write(f"  {line_str},\n")
            else:
                f.write(f"  {line_str}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_bikeshare_trips():
    """Generate bikeshare-trips.csv — 200K records, ~25MB"""
    rng = random.Random(SEED_BASE + 3)
    filepath = os.path.join(OUTPUT_DIR, "bikeshare-trips.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2025, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["trip_id", "start_station", "end_station", "start_time", "end_time",
                          "duration_min", "user_type", "bike_id"])
        for i in range(200000):
            tid = f"TRIP-{i + 1:07d}"
            start_st = rng.choice(BIKESHARE_STATION_IDS)
            end_st = rng.choice(BIKESHARE_STATION_IDS)
            while end_st == start_st:
                end_st = rng.choice(BIKESHARE_STATION_IDS)

            start_time = start_date + timedelta(minutes=rng.randint(0, 180 * 24 * 60))
            utype = rng.choices(USER_TYPES, weights=[0.65, 0.35], k=1)[0]

            if utype == "subscriber":
                duration = round(rng.uniform(5, 30), 1)
            else:
                duration = round(rng.uniform(10, 90), 1)

            end_time = start_time + timedelta(minutes=duration)
            bike = rng.choice(BIKE_IDS)

            writer.writerow([
                tid, start_st, end_st,
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration, utype, bike
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_passenger_complaints():
    """Generate passenger-complaints.json — 20K records, ~4MB"""
    rng = random.Random(SEED_BASE + 4)
    filepath = os.path.join(OUTPUT_DIR, "passenger-complaints.json")
    print(f"Generating {filepath}...")

    start_date = datetime(2025, 1, 1)
    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(20000):
            cid = f"COMP-{i + 1:06d}"
            ts = start_date + timedelta(hours=rng.randint(0, 180 * 24))
            route = rng.choice(ROUTE_IDS)
            category = rng.choices(COMPLAINT_CATEGORIES, weights=COMPLAINT_CATEGORY_WEIGHTS, k=1)[0]

            # Severity: delays tend to be higher severity
            if category == "delay":
                severity = rng.choices([1, 2, 3, 4, 5], weights=[0.05, 0.15, 0.30, 0.30, 0.20], k=1)[0]
            elif category == "safety":
                severity = rng.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.20, 0.35, 0.30], k=1)[0]
            else:
                severity = rng.choices([1, 2, 3, 4, 5], weights=[0.15, 0.25, 0.30, 0.20, 0.10], k=1)[0]

            desc_length = rng.randint(20, 500)

            record = {
                "complaint_id": cid,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "route_id": route,
                "category": category,
                "severity": severity,
                "description_length": desc_length
            }
            line = json.dumps(record)
            if i < 19999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_weather_hourly():
    """Generate weather-hourly.csv — 50K records, ~5MB"""
    rng = random.Random(SEED_BASE + 5)
    filepath = os.path.join(OUTPUT_DIR, "weather-hourly.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2025, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temp_f", "precipitation_in", "wind_mph", "condition"])
        for i in range(50000):
            ts = start_date + timedelta(hours=i % (180 * 24))
            month = ts.month

            base_temp = 72 + 18 * (1 - abs(month - 7) / 6.0)
            temp = round(base_temp + rng.uniform(-12, 12), 1)
            precip = round(max(0, rng.uniform(-0.3, 0.8)), 2) if rng.random() < 0.25 else 0.0
            wind = round(rng.uniform(0, 30), 1)
            condition = rng.choices(WEATHER_CONDITIONS, weights=WEATHER_CONDITION_WEIGHTS, k=1)[0]

            writer.writerow([ts.strftime("%Y-%m-%d %H:%M:%S"), temp, precip, wind, condition])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


if __name__ == "__main__":
    print("=" * 60)
    print("Project 02: CityTransit Mobility — Data Generation")
    print("=" * 60)
    generate_bus_telemetry()
    generate_rail_ridership()
    generate_bikeshare_trips()
    generate_passenger_complaints()
    generate_weather_hourly()
    print("\nAll files generated successfully!")
    total = sum(
        os.path.getsize(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith((".csv", ".json"))
    )
    print(f"Total size: {total / 1e6:.1f} MB")
