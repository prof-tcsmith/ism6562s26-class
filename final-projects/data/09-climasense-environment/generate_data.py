#!/usr/bin/env python3
"""
Generate synthetic datasets for ClimaSense Environment (Project 09).
Seed base: 2081. Target total: ~153 MB.

Usage: python3 generate_data.py
"""

import csv
import json
import os
import random
import math
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_BASE = 2081


# ---------------------------------------------------------------------------
# Shared reference data
# ---------------------------------------------------------------------------

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin",
    "Jacksonville", "San Jose", "Columbus", "Charlotte", "Denver"
]

# City center coordinates (approximate)
CITY_COORDS = {
    "New York": (40.71, -74.01), "Los Angeles": (34.05, -118.24),
    "Chicago": (41.88, -87.63), "Houston": (29.76, -95.37),
    "Phoenix": (33.45, -112.07), "Philadelphia": (39.95, -75.17),
    "San Antonio": (29.42, -98.49), "San Diego": (32.72, -117.16),
    "Dallas": (32.78, -96.80), "Austin": (30.27, -97.74),
    "Jacksonville": (30.33, -81.66), "San Jose": (37.34, -121.89),
    "Columbus": (39.96, -83.00), "Charlotte": (35.23, -80.84),
    "Denver": (39.74, -104.99)
}

# Stations per city (~33 each = ~500 total)
STATIONS = {}
STATION_LIST = []
for city in CITIES:
    lat_c, lon_c = CITY_COORDS[city]
    for i in range(1, 34):
        sid = f"{city[:3].upper()}-{i:03d}"
        STATIONS[sid] = {
            "city": city,
            "lat": round(lat_c + random.Random(hash(sid)).gauss(0, 0.05), 4),
            "lon": round(lon_c + random.Random(hash(sid)).gauss(0, 0.05), 4)
        }
        STATION_LIST.append(sid)

AQI_CATEGORIES = [
    (50, "good"), (100, "moderate"), (150, "unhealthy_sensitive"),
    (200, "unhealthy"), (300, "very_unhealthy"), (500, "hazardous")
]

ROAD_TYPES = ["highway", "arterial", "residential"]
CONGESTION_LEVELS = ["free", "moderate", "heavy", "gridlock"]

HEALTH_INCIDENT_TYPES = ["asthma_er_visit", "respiratory_admission", "heat_illness"]
AGE_GROUPS = ["0-17", "18-34", "35-49", "50-64", "65+"]

EMISSION_SOURCE_TYPES = ["industrial", "transportation", "residential", "construction"]


def aqi_category(aqi_val):
    for threshold, cat in AQI_CATEGORIES:
        if aqi_val <= threshold:
            return cat
    return "hazardous"


# ---------------------------------------------------------------------------
# 1. air-quality-readings.csv  (~85 MB, 500K records)
# ---------------------------------------------------------------------------

def generate_air_quality_readings():
    rng = random.Random(SEED_BASE + 1)
    outpath = os.path.join(SCRIPT_DIR, "air-quality-readings.csv")

    num_records = 800_000
    base_date = datetime(2024, 6, 1)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "station_id", "timestamp", "pm25", "pm10", "ozone_ppb",
            "no2_ppb", "so2_ppb", "co_ppm", "aqi_value", "aqi_category",
            "city", "lat", "lon"
        ])

        for _ in range(num_records):
            sid = rng.choice(STATION_LIST)
            info = STATIONS[sid]
            ts = base_date + timedelta(
                days=rng.randint(0, 365),
                hours=rng.randint(0, 23),
                minutes=rng.choice([0, 15, 30, 45])
            )

            # Diurnal pattern: worse during rush hours
            hour = ts.hour
            rush_factor = 1.0
            if 7 <= hour <= 9 or 16 <= hour <= 19:
                rush_factor = 1.4
            elif 10 <= hour <= 15:
                rush_factor = 1.1

            pm25 = round(max(0, rng.gauss(18, 12) * rush_factor), 1)
            pm10 = round(max(0, rng.gauss(35, 18) * rush_factor), 1)
            ozone = round(max(0, rng.gauss(35, 15)), 1)
            no2 = round(max(0, rng.gauss(22, 10) * rush_factor), 1)
            so2 = round(max(0, rng.gauss(5, 3)), 1)
            co = round(max(0, rng.gauss(0.5, 0.3) * rush_factor), 2)

            # AQI roughly driven by PM2.5
            aqi = int(max(0, min(500, pm25 * 2.5 + rng.gauss(10, 8))))
            cat = aqi_category(aqi)

            writer.writerow([
                sid, ts.strftime("%Y-%m-%d %H:%M:%S"),
                pm25, pm10, ozone, no2, so2, co,
                aqi, cat, info["city"],
                info["lat"], info["lon"]
            ])

    print(f"  air-quality-readings.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 2. weather-conditions.json  (~35 MB, 200K records)
# ---------------------------------------------------------------------------

def generate_weather_conditions():
    rng = random.Random(SEED_BASE + 2)
    outpath = os.path.join(SCRIPT_DIR, "weather-conditions.json")

    num_records = 350_000
    base_date = datetime(2024, 6, 1)

    records = []
    for _ in range(num_records):
        sid = rng.choice(STATION_LIST)
        ts = base_date + timedelta(
            days=rng.randint(0, 365),
            hours=rng.randint(0, 23),
            minutes=rng.choice([0, 15, 30, 45])
        )

        temp = round(rng.gauss(22, 10), 1)
        humidity = round(max(5, min(100, rng.gauss(55, 20))), 1)
        wind_speed = round(max(0, rng.gauss(3.5, 2.0)), 1)
        wind_dir = rng.randint(0, 359)
        pressure = round(rng.gauss(1013.25, 8), 1)
        precip = round(max(0, rng.expovariate(5)), 1)
        cloud = round(max(0, min(100, rng.gauss(45, 25))), 1)

        records.append({
            "station_id": sid,
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
            "temperature_c": temp,
            "humidity_pct": humidity,
            "wind_speed_ms": wind_speed,
            "wind_direction_deg": wind_dir,
            "pressure_hpa": pressure,
            "precipitation_mm": precip,
            "cloud_cover_pct": cloud
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  weather-conditions.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 3. traffic-counts.csv  (~25 MB, 150K records)
# ---------------------------------------------------------------------------

def generate_traffic_counts():
    rng = random.Random(SEED_BASE + 3)
    outpath = os.path.join(SCRIPT_DIR, "traffic-counts.csv")

    num_records = 250_000
    base_date = datetime(2024, 6, 1)

    # Traffic sensor IDs per city
    traffic_sensors = {}
    for city in CITIES:
        traffic_sensors[city] = [
            f"TS-{city[:3].upper()}-{j:03d}" for j in range(1, 51)
        ]

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "sensor_id", "city", "timestamp", "vehicle_count",
            "avg_speed_kmh", "truck_pct", "road_type", "congestion_level"
        ])

        for _ in range(num_records):
            city = rng.choice(CITIES)
            sensor = rng.choice(traffic_sensors[city])
            ts = base_date + timedelta(
                days=rng.randint(0, 365),
                hours=rng.randint(0, 23),
                minutes=rng.choice([0, 15, 30, 45])
            )

            hour = ts.hour
            if 7 <= hour <= 9 or 16 <= hour <= 19:
                vol_mult = 2.0
            elif 10 <= hour <= 15:
                vol_mult = 1.2
            elif 20 <= hour <= 23:
                vol_mult = 0.6
            else:
                vol_mult = 0.2

            road = rng.choice(ROAD_TYPES)
            if road == "highway":
                base_vol = 800
                base_speed = 95
            elif road == "arterial":
                base_vol = 400
                base_speed = 55
            else:
                base_vol = 100
                base_speed = 35

            vehicles = int(max(0, rng.gauss(base_vol * vol_mult, base_vol * 0.3)))
            speed = round(max(5, rng.gauss(
                base_speed * (1 / max(0.5, vol_mult * 0.6)), 10
            )), 1)
            truck = round(max(0, min(40, rng.gauss(12, 5))), 1)

            # Congestion level
            ratio = vehicles / (base_vol * 2.5) if base_vol > 0 else 0
            if ratio < 0.3:
                cong = "free"
            elif ratio < 0.6:
                cong = "moderate"
            elif ratio < 0.85:
                cong = "heavy"
            else:
                cong = "gridlock"

            writer.writerow([
                sensor, city, ts.strftime("%Y-%m-%d %H:%M:%S"),
                vehicles, speed, truck, road, cong
            ])

    print(f"  traffic-counts.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 4. health-incidents.json  (~5 MB, 30K records)
# ---------------------------------------------------------------------------

def generate_health_incidents():
    rng = random.Random(SEED_BASE + 4)
    outpath = os.path.join(SCRIPT_DIR, "health-incidents.json")

    num_records = 30_000
    base_date = datetime(2024, 6, 1)

    hospital_ids = {}
    for city in CITIES:
        hospital_ids[city] = [
            f"HOSP-{city[:3].upper()}-{j:02d}" for j in range(1, 8)
        ]

    records = []
    for i in range(num_records):
        city = rng.choice(CITIES)
        dt = base_date + timedelta(days=rng.randint(0, 365))
        inc_type = rng.choice(HEALTH_INCIDENT_TYPES)
        age = rng.choice(AGE_GROUPS)

        if inc_type == "asthma_er_visit":
            count = rng.randint(1, 25)
        elif inc_type == "respiratory_admission":
            count = rng.randint(1, 12)
        else:  # heat_illness
            count = rng.randint(0, 8)

        records.append({
            "incident_id": f"INC-{i + 1:06d}",
            "city": city,
            "date": dt.strftime("%Y-%m-%d"),
            "type": inc_type,
            "age_group": age,
            "count": count,
            "hospital_id": rng.choice(hospital_ids[city])
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  health-incidents.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 5. emission-sources.csv  (~3 MB, 20K records)
# ---------------------------------------------------------------------------

def generate_emission_sources():
    rng = random.Random(SEED_BASE + 5)
    outpath = os.path.join(SCRIPT_DIR, "emission-sources.csv")

    num_records = 20_000

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "source_id", "city", "type", "estimated_annual_tons",
            "lat", "lon", "permits_current"
        ])

        for i in range(num_records):
            city = rng.choice(CITIES)
            lat_c, lon_c = CITY_COORDS[city]
            stype = rng.choices(
                EMISSION_SOURCE_TYPES,
                weights=[20, 40, 25, 15],
                k=1
            )[0]

            if stype == "industrial":
                tons = round(rng.uniform(50, 5000), 1)
            elif stype == "transportation":
                tons = round(rng.uniform(10, 2000), 1)
            elif stype == "residential":
                tons = round(rng.uniform(1, 200), 1)
            else:
                tons = round(rng.uniform(5, 500), 1)

            lat = round(lat_c + rng.gauss(0, 0.08), 4)
            lon = round(lon_c + rng.gauss(0, 0.08), 4)
            permits = rng.choices([True, False], weights=[85, 15], k=1)[0]

            writer.writerow([
                f"SRC-{i + 1:05d}", city, stype, tons,
                lat, lon, permits
            ])

    print(f"  emission-sources.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating ClimaSense Environment datasets (seed base=2081)...")
    generate_air_quality_readings()
    generate_weather_conditions()
    generate_traffic_counts()
    generate_health_incidents()
    generate_emission_sources()
    print("Done.")
