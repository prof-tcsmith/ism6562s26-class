#!/usr/bin/env python3
"""
Generate datasets for Project 03: AgriFlow Farming
Target: ~150-200 MB total across all files
Seed base: 2021
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta

SEED_BASE = 2021
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

NUM_FARMS = 50
FARM_IDS = [f"FARM-{i:02d}" for i in range(1, NUM_FARMS + 1)]
FIELDS_PER_FARM = 20  # ~10 per farm average, up to 20
FIELD_IDS = []
FIELD_FARM_MAP = {}
rng_setup = random.Random(SEED_BASE)
for farm in FARM_IDS:
    n_fields = rng_setup.randint(8, 20)
    for j in range(1, n_fields + 1):
        fid = f"{farm}-F{j:02d}"
        FIELD_IDS.append(fid)
        FIELD_FARM_MAP[fid] = farm

NUM_SENSORS = 4000
SENSOR_IDS = [f"SOIL-{i:05d}" for i in range(1, NUM_SENSORS + 1)]
# Map sensors to fields
SENSOR_FIELD_MAP = {sid: FIELD_IDS[i % len(FIELD_IDS)] for i, sid in enumerate(SENSOR_IDS)}

CROP_TYPES = ["corn", "soybeans", "wheat"]
CROP_WEIGHTS = [0.40, 0.35, 0.25]

EQUIPMENT_TYPES = ["tractor", "harvester", "irrigator", "sprayer"]
EQUIPMENT_TYPE_WEIGHTS = [0.35, 0.20, 0.25, 0.20]
NUM_EQUIPMENT = 500
EQUIPMENT_IDS = [f"EQ-{i:04d}" for i in range(1, NUM_EQUIPMENT + 1)]
EQUIPMENT_FARM_MAP = {eid: FARM_IDS[i % NUM_FARMS] for i, eid in enumerate(EQUIPMENT_IDS)}

NUM_OPERATORS = 200
OPERATOR_IDS = [f"OP-{i:03d}" for i in range(1, NUM_OPERATORS + 1)]

REGIONS = ["midwest_north", "midwest_central", "midwest_south", "plains"]

NUM_WEATHER_STATIONS = 50
STATION_IDS = [f"WXFARM-{i:02d}" for i in range(1, NUM_WEATHER_STATIONS + 1)]
STATION_FARM_MAP = {sid: FARM_IDS[i % NUM_FARMS] for i, sid in enumerate(STATION_IDS)}


def generate_soil_sensors():
    """Generate soil-sensors.json — 400K records, ~70MB"""
    rng = random.Random(SEED_BASE + 1)
    filepath = os.path.join(OUTPUT_DIR, "soil-sensors.json")
    print(f"Generating {filepath}...")

    start_date = datetime(2024, 3, 1)  # Growing season start
    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(500000):
            sensor = rng.choice(SENSOR_IDS)
            field = SENSOR_FIELD_MAP[sensor]
            farm = FIELD_FARM_MAP[field]
            ts = start_date + timedelta(minutes=rng.randint(0, 210 * 24 * 60))  # ~7 months
            month = ts.month

            # Soil moisture: higher in spring, drops in summer without irrigation
            if month in (3, 4, 5):
                moisture = round(rng.uniform(25, 55), 1)
            elif month in (6, 7, 8):
                moisture = round(rng.uniform(12, 45), 1)
            else:
                moisture = round(rng.uniform(18, 50), 1)

            # Soil temperature follows air temp roughly
            base_soil_temp = 50 + 20 * (1 - abs(month - 7) / 5.0)
            soil_temp = round(base_soil_temp + rng.uniform(-8, 8), 1)

            ph = round(rng.uniform(5.5, 7.8), 2)
            nitrogen = round(rng.uniform(10, 80), 1)
            phosphorus = round(rng.uniform(5, 50), 1)
            potassium = round(rng.uniform(50, 250), 1)

            record = {
                "sensor_id": sensor,
                "farm_id": farm,
                "field_id": field,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "conditions": {
                    "soil_moisture_pct": moisture,
                    "soil_temp_f": soil_temp
                },
                "nutrients": {
                    "ph_level": ph,
                    "nitrogen_ppm": nitrogen,
                    "phosphorus_ppm": phosphorus,
                    "potassium_ppm": potassium
                }
            }
            line = json.dumps(record)
            if i < 499999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_crop_yields():
    """Generate crop-yields.csv — 100K records, ~15MB"""
    rng = random.Random(SEED_BASE + 2)
    filepath = os.path.join(OUTPUT_DIR, "crop-yields.csv")
    print(f"Generating {filepath}...")

    years = list(range(2017, 2025))  # 8 years
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["farm_id", "field_id", "year", "crop_type", "acres",
                          "yield_bushels_per_acre", "fertilizer_applied_lbs",
                          "irrigation_gallons", "planting_date", "harvest_date"])
        count = 0
        while count < 100000:
            for field in FIELD_IDS:
                if count >= 100000:
                    break
                for year in years:
                    if count >= 100000:
                        break
                    farm = FIELD_FARM_MAP[field]
                    crop = rng.choices(CROP_TYPES, weights=CROP_WEIGHTS, k=1)[0]
                    acres = rng.randint(20, 200)

                    # Yield depends on crop type
                    if crop == "corn":
                        base_yield = rng.uniform(140, 220)
                        plant_month, plant_day = 4, rng.randint(1, 30)
                        harvest_month, harvest_day = 10, rng.randint(1, 31)
                    elif crop == "soybeans":
                        base_yield = rng.uniform(35, 65)
                        plant_month, plant_day = 5, rng.randint(1, 31)
                        harvest_month, harvest_day = 10, rng.randint(1, 31)
                    else:  # wheat
                        base_yield = rng.uniform(40, 80)
                        plant_month, plant_day = 9, rng.randint(1, 30)
                        harvest_month = 6
                        harvest_day = rng.randint(1, 30)

                    # Add some variance
                    yield_bpa = round(base_yield * rng.uniform(0.7, 1.15), 1)
                    fertilizer = round(rng.uniform(100, 500) * acres / 100, 1)
                    irrigation = round(rng.uniform(5000, 50000) * acres / 100, 0)

                    try:
                        plant_date = datetime(year, plant_month, min(plant_day, 28))
                        harv_year = year if harvest_month > plant_month else year + 1
                        harvest_date = datetime(harv_year, harvest_month, min(harvest_day, 28))
                    except ValueError:
                        plant_date = datetime(year, plant_month, 15)
                        harvest_date = datetime(year, harvest_month, 15)

                    writer.writerow([
                        farm, field, year, crop, acres, yield_bpa,
                        fertilizer, int(irrigation),
                        plant_date.strftime("%Y-%m-%d"),
                        harvest_date.strftime("%Y-%m-%d")
                    ])
                    count += 1

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_weather_daily():
    """Generate weather-daily.csv — 150K records, ~20MB"""
    rng = random.Random(SEED_BASE + 3)
    filepath = os.path.join(OUTPUT_DIR, "weather-daily.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2017, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["station_id", "farm_id", "date", "high_temp_f", "low_temp_f",
                          "precipitation_in", "humidity_pct", "solar_radiation_wm2",
                          "wind_mph", "frost_risk"])
        for i in range(150000):
            station = rng.choice(STATION_IDS)
            farm = STATION_FARM_MAP[station]
            date = start_date + timedelta(days=rng.randint(0, 8 * 365))
            month = date.month

            # Temperature based on season (Midwest)
            base_high = 50 + 30 * (1 - abs(month - 7) / 6.0)
            high_temp = round(base_high + rng.uniform(-10, 10), 1)
            low_temp = round(high_temp - rng.uniform(10, 25), 1)

            precip = round(max(0, rng.uniform(-0.5, 1.5)), 2) if rng.random() < 0.3 else 0.0
            humidity = round(rng.uniform(30, 90), 1)
            solar = round(rng.uniform(50, 350), 1)
            wind = round(rng.uniform(2, 30), 1)
            frost_risk = low_temp < 35

            writer.writerow([
                station, farm, date.strftime("%Y-%m-%d"),
                high_temp, low_temp, precip, humidity, solar, wind,
                str(frost_risk).lower()
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_equipment_usage():
    """Generate equipment-usage.json — 80K records, ~15MB"""
    rng = random.Random(SEED_BASE + 4)
    filepath = os.path.join(OUTPUT_DIR, "equipment-usage.json")
    print(f"Generating {filepath}...")

    start_date = datetime(2024, 3, 1)
    with open(filepath, "w") as f:
        f.write("[\n")
        for i in range(80000):
            equip = rng.choice(EQUIPMENT_IDS)
            farm = EQUIPMENT_FARM_MAP[equip]
            # Pick a field from this farm
            farm_fields = [fid for fid in FIELD_IDS if FIELD_FARM_MAP[fid] == farm]
            field = rng.choice(farm_fields) if farm_fields else rng.choice(FIELD_IDS)

            ts = start_date + timedelta(hours=rng.randint(0, 210 * 24))
            etype = rng.choices(EQUIPMENT_TYPES, weights=EQUIPMENT_TYPE_WEIGHTS, k=1)[0]
            hours = round(rng.uniform(0.5, 12), 1)
            fuel = round(hours * rng.uniform(3, 15), 1)
            operator = rng.choice(OPERATOR_IDS)

            record = {
                "equipment_id": equip,
                "farm_id": farm,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "type": etype,
                "hours_operated": hours,
                "fuel_gallons": fuel,
                "field_id": field,
                "operator_id": operator
            }
            line = json.dumps(record)
            if i < 79999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_market_prices():
    """Generate market-prices.csv — 20K records, ~3MB"""
    rng = random.Random(SEED_BASE + 5)
    filepath = os.path.join(OUTPUT_DIR, "market-prices.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2017, 1, 1)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "crop_type", "price_per_bushel", "futures_price", "region"])
        for i in range(20000):
            date = start_date + timedelta(days=rng.randint(0, 8 * 365))
            crop = rng.choice(CROP_TYPES)
            region = rng.choice(REGIONS)

            if crop == "corn":
                base_price = rng.uniform(3.50, 7.00)
            elif crop == "soybeans":
                base_price = rng.uniform(8.00, 15.00)
            else:
                base_price = rng.uniform(4.00, 9.00)

            price = round(base_price + rng.uniform(-0.50, 0.50), 2)
            futures = round(price + rng.uniform(-0.30, 0.60), 2)

            writer.writerow([date.strftime("%Y-%m-%d"), crop, price, futures, region])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


if __name__ == "__main__":
    print("=" * 60)
    print("Project 03: AgriFlow Farming — Data Generation")
    print("=" * 60)
    generate_soil_sensors()
    generate_crop_yields()
    generate_weather_daily()
    generate_equipment_usage()
    generate_market_prices()
    print("\nAll files generated successfully!")
    total = sum(
        os.path.getsize(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith((".csv", ".json"))
    )
    print(f"Total size: {total / 1e6:.1f} MB")
