#!/usr/bin/env python3
"""
Generate synthetic datasets for PrecisionParts Manufacturing (Project 08).
Seed base: 2071. Target total: ~185 MB.

Usage: python3 generate_data.py
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_BASE = 2071


# ---------------------------------------------------------------------------
# Shared reference data
# ---------------------------------------------------------------------------

FACTORIES = [f"FAC-{i:02d}" for i in range(1, 9)]
FACTORY_LINES = {}  # Populated during init

PRODUCTS = [f"PROD-{i:04d}" for i in range(1, 201)]

SUPPLIERS = [f"SUP-{i:03d}" for i in range(1, 201)]

SUPPLIER_COUNTRIES = [
    "USA", "Mexico", "Canada", "Germany", "Japan", "China",
    "South Korea", "Taiwan", "India", "Brazil"
]

MACHINES = [f"MACH-{i:04d}" for i in range(1, 801)]

SHIFTS = ["day", "evening", "night"]

DEFECT_TYPES = ["dimensional", "surface", "material", "assembly", "none"]
DEFECT_SEVERITIES = ["critical", "major", "minor", "none"]

OPERATOR_IDS = [f"OP-{i:05d}" for i in range(1, 5001)]
INSPECTOR_IDS = [f"INSP-{i:04d}" for i in range(1, 201)]

WAREHOUSES = [f"WH-{i:03d}" for i in range(1, 51)]


def init_factory_lines(rng):
    """Create production lines per factory."""
    for fac in FACTORIES:
        n_lines = rng.randint(8, 15)
        FACTORY_LINES[fac] = [f"{fac}-LINE-{j:02d}" for j in range(1, n_lines + 1)]


# ---------------------------------------------------------------------------
# 1. production-lines.csv  (~80 MB, 500K records)
# ---------------------------------------------------------------------------

def generate_production_lines():
    rng = random.Random(SEED_BASE + 1)
    init_factory_lines(rng)
    outpath = os.path.join(SCRIPT_DIR, "production-lines.csv")

    num_records = 800_000
    base_date = datetime(2025, 1, 1)
    batch_counter = 0

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "line_id", "factory_id", "timestamp", "product_id", "batch_id",
            "cycle_time_sec", "units_produced", "defect_count", "operator_id",
            "shift", "machine_temp_c", "vibration_level"
        ])

        for _ in range(num_records):
            fac = rng.choice(FACTORIES)
            line = rng.choice(FACTORY_LINES[fac])
            ts = base_date + timedelta(
                days=rng.randint(0, 365),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59)
            )

            hour = ts.hour
            if 6 <= hour < 14:
                shift = "day"
            elif 14 <= hour < 22:
                shift = "evening"
            else:
                shift = "night"

            product = rng.choice(PRODUCTS)
            batch_counter += 1
            batch_id = f"BATCH-{batch_counter:07d}"
            cycle_time = round(max(5, rng.gauss(45, 12)), 1)
            units = rng.randint(50, 500)

            # Defect rate: higher on night shift, higher with elevated temp/vibration
            temp = round(max(15, min(120, rng.gauss(65, 12))), 1)
            vibration = round(max(0, rng.gauss(2.5, 1.0)), 2)

            base_defect_rate = 0.012
            if shift == "night":
                base_defect_rate *= 1.3
            if temp > 80:
                base_defect_rate *= 1.5
            if vibration > 3.5:
                base_defect_rate *= 1.4

            defects = 0
            for _ in range(units):
                if rng.random() < base_defect_rate:
                    defects += 1

            writer.writerow([
                line, fac, ts.strftime("%Y-%m-%d %H:%M:%S"), product,
                batch_id, cycle_time, units, defects,
                rng.choice(OPERATOR_IDS), shift, temp, vibration
            ])

    print(f"  production-lines.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 2. quality-inspections.json  (~20 MB, 100K records)
# ---------------------------------------------------------------------------

def generate_quality_inspections():
    rng = random.Random(SEED_BASE + 2)
    outpath = os.path.join(SCRIPT_DIR, "quality-inspections.json")

    num_records = 100_000
    base_date = datetime(2025, 1, 1)

    records = []
    for i in range(num_records):
        insp_id = f"INSP-{i + 1:07d}"
        batch_id = f"BATCH-{rng.randint(1, 500000):07d}"
        product = rng.choice(PRODUCTS)
        ts = base_date + timedelta(
            days=rng.randint(0, 365),
            hours=rng.randint(6, 22),
            minutes=rng.randint(0, 59)
        )
        inspector = rng.choice(INSPECTOR_IDS)

        defect_type = rng.choices(
            DEFECT_TYPES, weights=[10, 12, 8, 7, 63], k=1
        )[0]

        if defect_type == "none":
            severity = "none"
            dimension = round(rng.gauss(50.0, 0.05), 3)
            tolerance = 0.5
            deviation = round(abs(dimension - 50.0), 3)
        else:
            severity = rng.choices(
                ["critical", "major", "minor"], weights=[10, 35, 55], k=1
            )[0]
            if severity == "critical":
                dimension = round(rng.gauss(50.0, 1.2), 3)
            elif severity == "major":
                dimension = round(rng.gauss(50.0, 0.6), 3)
            else:
                dimension = round(rng.gauss(50.0, 0.3), 3)
            tolerance = 0.5
            deviation = round(abs(dimension - 50.0), 3)

        records.append({
            "inspection_id": insp_id,
            "batch_id": batch_id,
            "product_id": product,
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
            "inspector_id": inspector,
            "defect_type": defect_type,
            "severity": severity,
            "measurements": {
                "dimension_mm": dimension,
                "tolerance_mm": tolerance,
                "deviation_mm": deviation
            }
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  quality-inspections.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 3. inventory-levels.csv  (~30 MB, 200K records)
# ---------------------------------------------------------------------------

def generate_inventory_levels():
    rng = random.Random(SEED_BASE + 3)
    outpath = os.path.join(SCRIPT_DIR, "inventory-levels.csv")

    num_records = 200_000
    base_date = datetime(2025, 1, 1)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "warehouse_id", "product_id", "date", "quantity_on_hand",
            "quantity_reserved", "reorder_point", "lead_time_days",
            "unit_cost", "supplier_id"
        ])

        for _ in range(num_records):
            wh = rng.choice(WAREHOUSES)
            product = rng.choice(PRODUCTS)
            dt = base_date + timedelta(days=rng.randint(0, 365))
            on_hand = rng.randint(0, 5000)
            reserved = rng.randint(0, min(on_hand, 1000))
            reorder = rng.randint(100, 800)
            lead_time = rng.randint(3, 45)
            unit_cost = round(rng.uniform(0.50, 250.00), 2)
            supplier = rng.choice(SUPPLIERS)

            writer.writerow([
                wh, product, dt.strftime("%Y-%m-%d"), on_hand, reserved,
                reorder, lead_time, f"{unit_cost:.2f}", supplier
            ])

    print(f"  inventory-levels.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 4. supplier-performance.json  (~10 MB, 50K records)
# ---------------------------------------------------------------------------

def generate_supplier_performance():
    rng = random.Random(SEED_BASE + 4)
    outpath = os.path.join(SCRIPT_DIR, "supplier-performance.json")

    num_records = 50_000
    base_date = datetime(2024, 1, 1)

    # Assign each supplier a country
    supplier_countries = {}
    for sup in SUPPLIERS:
        supplier_countries[sup] = rng.choice(SUPPLIER_COUNTRIES)

    records = []
    for i in range(num_records):
        supplier = rng.choice(SUPPLIERS)
        order_id = f"ORD-{i + 1:06d}"
        expected = base_date + timedelta(days=rng.randint(0, 730))
        delay_days = rng.choices(
            [0, 0, 0, 1, 2, 3, 5, 7, 14],
            weights=[40, 15, 10, 10, 8, 7, 5, 3, 2],
            k=1
        )[0]
        actual = expected + timedelta(days=delay_days)
        qty_ordered = rng.randint(100, 10000)
        # Quantity delivered may be less
        qty_delivered = qty_ordered - rng.choices(
            [0, 0, 0, rng.randint(1, 50), rng.randint(50, 500)],
            weights=[60, 15, 10, 10, 5],
            k=1
        )[0]
        qty_delivered = max(0, qty_delivered)
        quality = rng.randint(3, 10)

        records.append({
            "supplier_id": supplier,
            "delivery_date": actual.strftime("%Y-%m-%d"),
            "order_id": order_id,
            "expected_date": expected.strftime("%Y-%m-%d"),
            "actual_date": actual.strftime("%Y-%m-%d"),
            "quantity_ordered": qty_ordered,
            "quantity_delivered": qty_delivered,
            "quality_score": quality,
            "country": supplier_countries[supplier]
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  supplier-performance.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 5. equipment-sensors.csv  (~45 MB, 300K records)
# ---------------------------------------------------------------------------

def generate_equipment_sensors():
    rng = random.Random(SEED_BASE + 5)
    outpath = os.path.join(SCRIPT_DIR, "equipment-sensors.csv")

    num_records = 500_000
    base_date = datetime(2025, 1, 1)

    # Assign machines to factories
    machine_factory = {}
    machines_list = list(MACHINES)
    rng.shuffle(machines_list)
    per_factory = len(machines_list) // len(FACTORIES)
    for i, fac in enumerate(FACTORIES):
        for m in machines_list[i * per_factory:(i + 1) * per_factory]:
            machine_factory[m] = fac

    statuses = ["running", "idle", "maintenance"]

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "machine_id", "factory_id", "timestamp", "temperature_c",
            "vibration_mm_s", "power_consumption_kw", "oil_pressure_psi",
            "status"
        ])

        for _ in range(num_records):
            machine = rng.choice(machines_list)
            fac = machine_factory.get(machine, rng.choice(FACTORIES))
            ts = base_date + timedelta(
                days=rng.randint(0, 365),
                hours=rng.randint(0, 23),
                minutes=rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]),
                seconds=rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
            )

            status = rng.choices(
                statuses, weights=[75, 15, 10], k=1
            )[0]

            if status == "running":
                temp = round(max(20, rng.gauss(68, 10)), 1)
                vibration = round(max(0, rng.gauss(2.8, 0.8)), 2)
                power = round(max(0.5, rng.gauss(15, 5)), 1)
                oil = round(max(20, rng.gauss(55, 8)), 1)
            elif status == "idle":
                temp = round(max(18, rng.gauss(30, 5)), 1)
                vibration = round(max(0, rng.gauss(0.3, 0.1)), 2)
                power = round(max(0, rng.gauss(1.5, 0.5)), 1)
                oil = round(max(15, rng.gauss(45, 5)), 1)
            else:  # maintenance
                temp = round(max(15, rng.gauss(25, 3)), 1)
                vibration = 0.0
                power = 0.0
                oil = round(max(10, rng.gauss(40, 8)), 1)

            writer.writerow([
                machine, fac, ts.strftime("%Y-%m-%d %H:%M:%S"),
                temp, vibration, power, oil, status
            ])

    print(f"  equipment-sensors.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating PrecisionParts Manufacturing datasets (seed base=2071)...")
    generate_production_lines()
    generate_quality_inspections()
    generate_inventory_levels()
    generate_supplier_performance()
    generate_equipment_sensors()
    print("Done.")
