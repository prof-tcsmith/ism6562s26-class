#!/usr/bin/env python3
"""
Generate datasets for Project 01: SmartGrid Energy (VoltEdge Power)
Target: ~150-200 MB total across all files
Seed base: 2001
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta

SEED_BASE = 2001
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

GRID_ZONES = [f"ZONE-{i:02d}" for i in range(1, 15)]  # 14 zones
CUSTOMER_TYPES = ["residential", "commercial", "industrial"]
CUSTOMER_TYPE_WEIGHTS = [0.70, 0.22, 0.08]
OUTAGE_CAUSES = ["weather", "equipment", "overload", "animal", "unknown"]
OUTAGE_CAUSE_WEIGHTS = [0.35, 0.28, 0.22, 0.08, 0.07]
SENSOR_STATUSES = ["normal", "warning", "critical"]
SENSOR_STATUS_WEIGHTS = [0.85, 0.12, 0.03]
MAINTENANCE_TYPES = ["preventive", "corrective", "emergency"]
MAINTENANCE_TYPE_WEIGHTS = [0.45, 0.35, 0.20]
WEATHER_CONDITIONS = ["clear", "cloudy", "rain", "heavy_rain", "storm", "snow", "fog"]
WEATHER_CONDITION_WEIGHTS = [0.35, 0.25, 0.15, 0.08, 0.05, 0.07, 0.05]

NUM_TRANSFORMERS = 2000
TRANSFORMER_IDS = [f"T-{i:04d}" for i in range(1, NUM_TRANSFORMERS + 1)]
NUM_SENSORS = 8000
SENSOR_IDS = [f"S-{i:05d}" for i in range(1, NUM_SENSORS + 1)]
NUM_METERS = 50000
METER_IDS = [f"M-{i:06d}" for i in range(1, NUM_METERS + 1)]
NUM_WEATHER_STATIONS = 14
STATION_IDS = [f"WS-{i:02d}" for i in range(1, NUM_WEATHER_STATIONS + 1)]
NUM_TECHNICIANS = 120
TECHNICIAN_IDS = [f"TECH-{i:03d}" for i in range(1, NUM_TECHNICIANS + 1)]

# Map sensors and transformers to zones
SENSOR_ZONE_MAP = {sid: GRID_ZONES[i % len(GRID_ZONES)] for i, sid in enumerate(SENSOR_IDS)}
TRANSFORMER_ZONE_MAP = {tid: GRID_ZONES[i % len(GRID_ZONES)] for i, tid in enumerate(TRANSFORMER_IDS)}
SENSOR_TRANSFORMER_MAP = {sid: TRANSFORMER_IDS[i % NUM_TRANSFORMERS] for i, sid in enumerate(SENSOR_IDS)}
STATION_ZONE_MAP = {sid: GRID_ZONES[i] for i, sid in enumerate(STATION_IDS)}
METER_ZONE_MAP = {mid: GRID_ZONES[i % len(GRID_ZONES)] for i, mid in enumerate(METER_IDS)}


def generate_power_consumption():
    """Generate power-consumption.csv — 500K records, ~80MB"""
    rng = random.Random(SEED_BASE + 1)
    filepath = os.path.join(OUTPUT_DIR, "power-consumption.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2023, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["meter_id", "timestamp", "kwh_reading", "customer_type", "grid_zone", "temperature_f"])
        for i in range(1300000):
            meter = rng.choice(METER_IDS)
            ts = start_date + timedelta(minutes=rng.randint(0, 365 * 24 * 60))
            hour = ts.hour
            month = ts.month

            ctype = rng.choices(CUSTOMER_TYPES, weights=CUSTOMER_TYPE_WEIGHTS, k=1)[0]

            # Base consumption varies by type
            if ctype == "residential":
                base = rng.uniform(0.5, 4.0)
            elif ctype == "commercial":
                base = rng.uniform(5.0, 25.0)
            else:
                base = rng.uniform(20.0, 100.0)

            # Peak hours boost
            if 14 <= hour <= 19:
                base *= rng.uniform(1.3, 1.8)
            elif 6 <= hour <= 9:
                base *= rng.uniform(1.1, 1.4)

            # Seasonal variation
            if month in (6, 7, 8):  # summer
                base *= rng.uniform(1.2, 1.6)
            elif month in (12, 1, 2):  # winter
                base *= rng.uniform(1.1, 1.4)

            kwh = round(base, 3)
            zone = METER_ZONE_MAP[meter]

            # Temperature correlated with season
            base_temp = 60 + 25 * (1 - abs(month - 7) / 6.0)
            temp = round(base_temp + rng.uniform(-15, 15), 1)

            writer.writerow([meter, ts.strftime("%Y-%m-%d %H:%M:%S"), kwh, ctype, zone, temp])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_grid_sensors():
    """Generate grid-sensors.json — 200K records, ~40MB"""
    rng = random.Random(SEED_BASE + 2)
    filepath = os.path.join(OUTPUT_DIR, "grid-sensors.json")
    print(f"Generating {filepath}...")

    start_date = datetime(2023, 1, 1)
    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(400000):
            sensor = rng.choice(SENSOR_IDS)
            ts = start_date + timedelta(seconds=rng.randint(0, 365 * 24 * 3600))
            zone = SENSOR_ZONE_MAP[sensor]
            transformer = SENSOR_TRANSFORMER_MAP[sensor]
            status = rng.choices(SENSOR_STATUSES, weights=SENSOR_STATUS_WEIGHTS, k=1)[0]

            # Voltage: nominal 120V, varies by status
            if status == "critical":
                voltage = round(rng.uniform(95, 108) if rng.random() < 0.5 else rng.uniform(132, 145), 2)
            elif status == "warning":
                voltage = round(rng.uniform(108, 112) if rng.random() < 0.5 else rng.uniform(128, 132), 2)
            else:
                voltage = round(rng.uniform(115, 125), 2)

            current = round(rng.uniform(5, 200), 2)
            frequency = round(rng.uniform(59.90, 60.10), 3)
            if status == "critical":
                frequency = round(rng.uniform(59.70, 59.90) if rng.random() < 0.5 else rng.uniform(60.10, 60.30), 3)

            record = {
                "sensor_id": sensor,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "grid_zone": zone,
                "transformer_id": transformer,
                "status": status,
                "readings": {
                    "voltage": voltage,
                    "current_amps": current,
                    "frequency_hz": frequency
                }
            }
            line = json.dumps(record)
            if i < 399999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_outage_history():
    """Generate outage-history.csv — 50K records, ~8MB"""
    rng = random.Random(SEED_BASE + 3)
    filepath = os.path.join(OUTPUT_DIR, "outage-history.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2021, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["outage_id", "start_time", "end_time", "grid_zone", "cause",
                          "customers_affected", "duration_minutes"])
        for i in range(50000):
            oid = f"OUT-{i + 1:06d}"
            zone = rng.choice(GRID_ZONES)
            cause = rng.choices(OUTAGE_CAUSES, weights=OUTAGE_CAUSE_WEIGHTS, k=1)[0]

            start = start_date + timedelta(minutes=rng.randint(0, 3 * 365 * 24 * 60))

            if cause == "weather":
                duration = rng.randint(30, 2880)  # up to 2 days
                affected = rng.randint(50, 5000)
            elif cause == "equipment":
                duration = rng.randint(60, 1440)
                affected = rng.randint(20, 2000)
            elif cause == "overload":
                duration = rng.randint(15, 240)
                affected = rng.randint(100, 3000)
            elif cause == "animal":
                duration = rng.randint(10, 120)
                affected = rng.randint(5, 500)
            else:
                duration = rng.randint(15, 480)
                affected = rng.randint(10, 1000)

            end = start + timedelta(minutes=duration)

            writer.writerow([
                oid, start.strftime("%Y-%m-%d %H:%M:%S"),
                end.strftime("%Y-%m-%d %H:%M:%S"),
                zone, cause, affected, duration
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_weather_stations():
    """Generate weather-stations.json — 100K records, ~15MB"""
    rng = random.Random(SEED_BASE + 4)
    filepath = os.path.join(OUTPUT_DIR, "weather-stations.json")
    print(f"Generating {filepath}...")

    start_date = datetime(2023, 1, 1)
    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(100000):
            station = rng.choice(STATION_IDS)
            ts = start_date + timedelta(hours=rng.randint(0, 365 * 24))
            zone = STATION_ZONE_MAP[station]
            month = ts.month

            # Season-based temperature
            base_temp = 60 + 25 * (1 - abs(month - 7) / 6.0)
            temp = round(base_temp + rng.uniform(-15, 15), 1)

            humidity = round(rng.uniform(20, 95), 1)
            wind = round(rng.uniform(0, 45), 1)
            precip = round(max(0, rng.uniform(-0.5, 1.5)), 2) if rng.random() < 0.3 else 0.0
            condition = rng.choices(WEATHER_CONDITIONS, weights=WEATHER_CONDITION_WEIGHTS, k=1)[0]

            record = {
                "station_id": station,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "temp_f": temp,
                "humidity": humidity,
                "wind_speed_mph": wind,
                "precipitation_in": precip,
                "condition": condition,
                "grid_zone": zone
            }
            line = json.dumps(record)
            if i < 99999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_maintenance_logs():
    """Generate maintenance-logs.csv — 30K records, ~5MB"""
    rng = random.Random(SEED_BASE + 5)
    filepath = os.path.join(OUTPUT_DIR, "maintenance-logs.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2021, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["work_order_id", "transformer_id", "date", "type", "cost",
                          "technician_id", "resolution_time_hours"])
        for i in range(30000):
            woid = f"WO-{i + 1:06d}"
            transformer = rng.choice(TRANSFORMER_IDS)
            date = start_date + timedelta(days=rng.randint(0, 3 * 365))
            mtype = rng.choices(MAINTENANCE_TYPES, weights=MAINTENANCE_TYPE_WEIGHTS, k=1)[0]

            if mtype == "preventive":
                cost = round(rng.uniform(200, 2000), 2)
                resolution = round(rng.uniform(1, 8), 1)
            elif mtype == "corrective":
                cost = round(rng.uniform(500, 8000), 2)
                resolution = round(rng.uniform(2, 24), 1)
            else:
                cost = round(rng.uniform(2000, 25000), 2)
                resolution = round(rng.uniform(0.5, 48), 1)

            tech = rng.choice(TECHNICIAN_IDS)

            writer.writerow([
                woid, transformer, date.strftime("%Y-%m-%d"),
                mtype, cost, tech, resolution
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


if __name__ == "__main__":
    print("=" * 60)
    print("Project 01: SmartGrid Energy — Data Generation")
    print("=" * 60)
    generate_power_consumption()
    generate_grid_sensors()
    generate_outage_history()
    generate_weather_stations()
    generate_maintenance_logs()
    print("\nAll files generated successfully!")
    total = sum(
        os.path.getsize(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith((".csv", ".json"))
    )
    print(f"Total size: {total / 1e6:.1f} MB")
