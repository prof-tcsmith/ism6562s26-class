#!/usr/bin/env python3
"""
Generate datasets for Project 05: FinPulse Fraud Detection
Target: ~150-200 MB total across all files
Seed base: 2041
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta

SEED_BASE = 2041
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

NUM_CUSTOMERS = 100000
CUSTOMER_IDS = [f"CUST-{i:06d}" for i in range(1, NUM_CUSTOMERS + 1)]
CARD_IDS = [f"CARD-{i:06d}" for i in range(1, NUM_CUSTOMERS + 1)]  # 1:1 with customers
CUSTOMER_CARD_MAP = dict(zip(CUSTOMER_IDS, CARD_IDS))

NUM_MERCHANTS = 10000
MERCHANT_IDS = [f"MERCH-{i:05d}" for i in range(1, NUM_MERCHANTS + 1)]

MERCHANT_CATEGORIES = [
    "retail", "grocery", "restaurant", "gas_station", "online_marketplace",
    "electronics", "travel", "entertainment", "healthcare", "subscription_service",
    "luxury_goods", "gambling", "digital_goods", "money_transfer", "jewelry"
]
MERCHANT_CAT_WEIGHTS = [0.15, 0.14, 0.12, 0.10, 0.10, 0.08, 0.06, 0.05, 0.05,
                        0.04, 0.03, 0.02, 0.02, 0.02, 0.02]

# High fraud risk categories
HIGH_RISK_CATEGORIES = {"gambling", "money_transfer", "digital_goods", "luxury_goods", "jewelry"}

COUNTRIES = ["US", "CA", "UK", "DE", "FR", "BR", "MX", "IN", "CN", "NG", "RU", "JP", "AU"]
HOME_COUNTRY_WEIGHTS = [0.50, 0.12, 0.12, 0.08, 0.04, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01, 0.02, 0.02]
CHANNELS = ["online", "in_store", "atm", "contactless"]
CHANNEL_WEIGHTS = [0.40, 0.30, 0.10, 0.20]
CURRENCIES = ["USD", "CAD", "GBP", "EUR"]
CURRENCY_WEIGHTS = [0.55, 0.15, 0.15, 0.15]

INCOME_BRACKETS = ["low", "medium", "high", "very_high"]
INCOME_WEIGHTS = [0.25, 0.40, 0.25, 0.10]

FRAUD_TYPES = ["card_not_present", "counterfeit", "account_takeover", "identity_theft"]
FRAUD_TYPE_WEIGHTS = [0.62, 0.11, 0.21, 0.06]
REPORTED_BY = ["customer", "bank", "merchant"]
REPORTED_BY_WEIGHTS = [0.55, 0.30, 0.15]
RESOLUTIONS = ["confirmed_fraud", "false_alarm"]

DEVICE_TYPES = ["mobile", "desktop", "tablet"]
DEVICE_WEIGHTS = [0.45, 0.40, 0.15]
OS_LIST = ["iOS", "Android", "Windows", "macOS", "Linux"]
OS_WEIGHTS = [0.25, 0.22, 0.30, 0.18, 0.05]
BROWSERS = ["Chrome", "Safari", "Firefox", "Edge", "Samsung_Internet", "Opera"]
BROWSER_WEIGHTS = [0.40, 0.25, 0.12, 0.10, 0.08, 0.05]

# Pre-assign customer attributes
rng_setup = random.Random(SEED_BASE)
CUSTOMER_ATTRS = {}
for cid in CUSTOMER_IDS:
    home = rng_setup.choices(COUNTRIES, weights=HOME_COUNTRY_WEIGHTS, k=1)[0]
    income = rng_setup.choices(INCOME_BRACKETS, weights=INCOME_WEIGHTS, k=1)[0]
    age = rng_setup.randint(18, 85)
    acct_age = rng_setup.randint(1, 120)

    if income == "low":
        avg_spend = round(rng_setup.uniform(200, 1500), 2)
        credit_limit = rng_setup.randint(1000, 5000)
    elif income == "medium":
        avg_spend = round(rng_setup.uniform(800, 4000), 2)
        credit_limit = rng_setup.randint(3000, 15000)
    elif income == "high":
        avg_spend = round(rng_setup.uniform(2000, 10000), 2)
        credit_limit = rng_setup.randint(10000, 50000)
    else:
        avg_spend = round(rng_setup.uniform(5000, 30000), 2)
        credit_limit = rng_setup.randint(25000, 100000)

    n_cats = rng_setup.randint(2, 5)
    typical = rng_setup.sample(MERCHANT_CATEGORIES, k=n_cats)

    CUSTOMER_ATTRS[cid] = {
        "home_country": home, "income_bracket": income, "age": age,
        "account_age_months": acct_age, "avg_monthly_spend": avg_spend,
        "credit_limit": credit_limit, "typical_categories": typical
    }

# Pre-assign merchant attributes
MERCHANT_ATTRS = {}
for mid in MERCHANT_IDS:
    cat = rng_setup.choices(MERCHANT_CATEGORIES, weights=MERCHANT_CAT_WEIGHTS, k=1)[0]
    country = rng_setup.choices(COUNTRIES, weights=HOME_COUNTRY_WEIGHTS, k=1)[0]
    risk = rng_setup.randint(6, 10) if cat in HIGH_RISK_CATEGORIES else rng_setup.randint(1, 7)
    avg_txn = round(rng_setup.uniform(5, 500), 2)
    monthly_vol = rng_setup.randint(100, 50000)
    name = f"Merchant_{mid.split('-')[1]}"
    MERCHANT_ATTRS[mid] = {
        "name": name, "category": cat, "country": country,
        "risk_score": risk, "avg_transaction_amount": avg_txn,
        "monthly_volume": monthly_vol
    }


def generate_transactions():
    """Generate transactions.csv — 500K records, ~80MB"""
    rng = random.Random(SEED_BASE + 1)
    filepath = os.path.join(OUTPUT_DIR, "transactions.csv")
    print(f"Generating {filepath}...")

    start_date = datetime(2025, 1, 1)
    # Track which txn_ids are fraud for fraud-reports
    fraud_txn_ids = []

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["txn_id", "timestamp", "card_id", "merchant_id", "amount",
                          "currency", "merchant_category", "country", "channel",
                          "is_international"])
        for i in range(1000000):
            txn_id = f"TXN-{i + 1:07d}"
            customer = rng.choice(CUSTOMER_IDS)
            card = CUSTOMER_CARD_MAP[customer]
            merchant = rng.choice(MERCHANT_IDS)
            m_attrs = MERCHANT_ATTRS[merchant]
            c_attrs = CUSTOMER_ATTRS[customer]

            ts = start_date + timedelta(seconds=rng.randint(0, 180 * 24 * 3600))
            channel = rng.choices(CHANNELS, weights=CHANNEL_WEIGHTS, k=1)[0]
            currency = rng.choices(CURRENCIES, weights=CURRENCY_WEIGHTS, k=1)[0]
            country = m_attrs["country"]
            is_international = country != c_attrs["home_country"]
            category = m_attrs["category"]

            # Amount: based on merchant avg with variance
            base_amount = m_attrs["avg_transaction_amount"]
            amount = round(max(0.50, base_amount * rng.uniform(0.2, 3.0)), 2)

            # ~2% fraud rate — higher for high-risk categories and international
            fraud_prob = 0.015
            if category in HIGH_RISK_CATEGORIES:
                fraud_prob += 0.02
            if is_international:
                fraud_prob += 0.01
            if channel == "online":
                fraud_prob += 0.005

            is_fraud = rng.random() < fraud_prob
            if is_fraud:
                # Fraud transactions tend to be larger or in unusual patterns
                amount = round(amount * rng.uniform(1.5, 5.0), 2)
                fraud_txn_ids.append(txn_id)

            writer.writerow([
                txn_id, ts.strftime("%Y-%m-%d %H:%M:%S"),
                card, merchant, amount, currency,
                category, country, channel,
                str(is_international).lower()
            ])

    # Save fraud IDs for fraud-reports generation
    with open(os.path.join(OUTPUT_DIR, ".fraud_ids.tmp"), "w") as f:
        json.dump(fraud_txn_ids, f)

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")
    print(f"  Fraud transactions: {len(fraud_txn_ids)}")


def generate_customer_profiles():
    """Generate customer-profiles.json — 100K records, ~20MB"""
    rng = random.Random(SEED_BASE + 2)
    filepath = os.path.join(OUTPUT_DIR, "customer-profiles.json")
    print(f"Generating {filepath}...")

    with open(filepath, "w") as f:
        f.write("[\n")
        for idx, cid in enumerate(CUSTOMER_IDS):
            attrs = CUSTOMER_ATTRS[cid]
            record = {
                "customer_id": cid,
                "card_id": CUSTOMER_CARD_MAP[cid],
                "age": attrs["age"],
                "income_bracket": attrs["income_bracket"],
                "account_age_months": attrs["account_age_months"],
                "avg_monthly_spend": attrs["avg_monthly_spend"],
                "home_country": attrs["home_country"],
                "typical_categories": attrs["typical_categories"],
                "credit_limit": attrs["credit_limit"]
            }
            line = json.dumps(record)
            if idx < NUM_CUSTOMERS - 1:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_merchant_directory():
    """Generate merchant-directory.csv — 10K records, ~2MB"""
    rng = random.Random(SEED_BASE + 3)
    filepath = os.path.join(OUTPUT_DIR, "merchant-directory.csv")
    print(f"Generating {filepath}...")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["merchant_id", "name", "category", "country", "risk_score",
                          "avg_transaction_amount", "monthly_volume"])
        for mid in MERCHANT_IDS:
            attrs = MERCHANT_ATTRS[mid]
            writer.writerow([
                mid, attrs["name"], attrs["category"], attrs["country"],
                attrs["risk_score"], attrs["avg_transaction_amount"],
                attrs["monthly_volume"]
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_fraud_reports():
    """Generate fraud-reports.json — 15K records, ~3MB"""
    rng = random.Random(SEED_BASE + 4)
    filepath = os.path.join(OUTPUT_DIR, "fraud-reports.json")
    print(f"Generating {filepath}...")

    # Load fraud transaction IDs
    fraud_ids_path = os.path.join(OUTPUT_DIR, ".fraud_ids.tmp")
    if os.path.exists(fraud_ids_path):
        with open(fraud_ids_path) as f:
            fraud_txn_ids = json.load(f)
    else:
        # Fallback: generate dummy IDs
        fraud_txn_ids = [f"TXN-{rng.randint(1, 1000000):07d}" for _ in range(15000)]

    start_date = datetime(2025, 1, 1)

    with open(filepath, "w") as f:
        f.write("[\n")
        count = min(15000, len(fraud_txn_ids))
        selected = rng.sample(fraud_txn_ids, k=count) if len(fraud_txn_ids) >= count else fraud_txn_ids

        # Also add some false alarms
        while len(selected) < 15000:
            selected.append(f"TXN-{rng.randint(1, 1000000):07d}")

        for i, txn_id in enumerate(selected[:15000]):
            rid = f"FR-{i + 1:06d}"
            ts = start_date + timedelta(hours=rng.randint(0, 180 * 24))
            reported_by = rng.choices(REPORTED_BY, weights=REPORTED_BY_WEIGHTS, k=1)[0]
            fraud_type = rng.choices(FRAUD_TYPES, weights=FRAUD_TYPE_WEIGHTS, k=1)[0]
            amount = round(rng.uniform(10, 5000), 2)

            # Most reports from fraud txns are confirmed; false alarms from non-fraud
            if txn_id in fraud_txn_ids:
                resolution = rng.choices(RESOLUTIONS, weights=[0.85, 0.15], k=1)[0]
            else:
                resolution = rng.choices(RESOLUTIONS, weights=[0.20, 0.80], k=1)[0]

            record = {
                "report_id": rid,
                "txn_id": txn_id,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "reported_by": reported_by,
                "fraud_type": fraud_type,
                "amount_disputed": amount,
                "resolution": resolution
            }
            line = json.dumps(record)
            if i < 14999:
                f.write(f"  {line},\n")
            else:
                f.write(f"  {line}\n")
        f.write("]\n")

    # Clean up temp file
    if os.path.exists(fraud_ids_path):
        os.remove(fraud_ids_path)

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


def generate_device_fingerprints():
    """Generate device-fingerprints.csv — 300K records, ~40MB"""
    rng = random.Random(SEED_BASE + 5)
    filepath = os.path.join(OUTPUT_DIR, "device-fingerprints.csv")
    print(f"Generating {filepath}...")

    # Load fraud IDs if available for correlation
    fraud_ids_path = os.path.join(OUTPUT_DIR, ".fraud_ids.tmp")
    fraud_set = set()
    if os.path.exists(fraud_ids_path):
        with open(fraud_ids_path) as f:
            fraud_set = set(json.load(f))

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["session_id", "txn_id", "device_type", "os", "browser",
                          "ip_country", "ip_city", "is_vpn", "is_known_device",
                          "login_attempt_count"])

        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Toronto",
                  "London", "Berlin", "Paris", "Mumbai", "Tokyo",
                  "Sao Paulo", "Mexico City", "Lagos", "Moscow", "Sydney",
                  "San Francisco", "Dallas", "Miami", "Vancouver", "Manchester"]

        for i in range(600000):
            sess_id = f"DSESS-{i + 1:07d}"
            txn_id = f"TXN-{rng.randint(1, 1000000):07d}"

            device = rng.choices(DEVICE_TYPES, weights=DEVICE_WEIGHTS, k=1)[0]
            os_type = rng.choices(OS_LIST, weights=OS_WEIGHTS, k=1)[0]
            browser = rng.choices(BROWSERS, weights=BROWSER_WEIGHTS, k=1)[0]

            ip_country = rng.choices(COUNTRIES, weights=HOME_COUNTRY_WEIGHTS, k=1)[0]
            ip_city = rng.choice(cities)

            # Fraud-associated sessions more likely to use VPN and unknown devices
            is_fraud_related = txn_id in fraud_set
            if is_fraud_related:
                is_vpn = rng.random() < 0.40
                is_known = rng.random() < 0.25
                login_attempts = rng.randint(1, 8)
            else:
                is_vpn = rng.random() < 0.08
                is_known = rng.random() < 0.85
                login_attempts = rng.choices([1, 1, 1, 2, 3], k=1)[0]

            writer.writerow([
                sess_id, txn_id, device, os_type, browser,
                ip_country, ip_city,
                str(is_vpn).lower(), str(is_known).lower(),
                login_attempts
            ])

    print(f"  Done: {os.path.getsize(filepath) / 1e6:.1f} MB")


if __name__ == "__main__":
    print("=" * 60)
    print("Project 05: FinPulse Fraud Detection — Data Generation")
    print("=" * 60)
    generate_transactions()
    generate_customer_profiles()
    generate_merchant_directory()
    generate_fraud_reports()
    generate_device_fingerprints()
    print("\nAll files generated successfully!")
    total = sum(
        os.path.getsize(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith((".csv", ".json"))
    )
    print(f"Total size: {total / 1e6:.1f} MB")
