#!/usr/bin/env python3
"""
Generate synthetic datasets for MediaWave Streaming (Project 10).
Seed base: 2091. Target total: ~210 MB.

Usage: python3 generate_data.py
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_BASE = 2091


# ---------------------------------------------------------------------------
# Shared reference data
# ---------------------------------------------------------------------------

GENRES = [
    "drama", "comedy", "action", "thriller", "sci_fi", "horror",
    "documentary", "romance", "animation", "crime", "fantasy",
    "mystery", "adventure", "indie", "international"
]

RATINGS = ["G", "PG", "PG13", "R"]

LANGUAGES = [
    "English", "Spanish", "French", "Korean", "Japanese",
    "German", "Portuguese", "Hindi", "Mandarin", "Italian"
]

COUNTRIES = [
    "USA", "UK", "South Korea", "Japan", "France", "Germany",
    "Brazil", "India", "Mexico", "Spain", "Canada", "Australia"
]

DEVICES = ["smart_tv", "mobile", "tablet", "laptop", "console"]
QUALITY_LEVELS = ["sd", "hd", "4k"]

PLAN_TYPES = ["basic", "standard", "premium"]

USER_ACTIONS = [
    "browse", "search", "play", "pause", "skip",
    "rate", "add_watchlist", "share"
]

CDN_REGIONS = [
    "us-east", "us-west", "us-central", "eu-west", "eu-central",
    "asia-pacific", "south-america"
]

ISPS = [
    "Comcast", "AT&T", "Verizon", "Charter", "T-Mobile",
    "Cox", "CenturyLink", "Frontier", "Windstream", "Other"
]

AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

USER_COUNTRIES = [
    "USA", "Canada", "UK", "Australia", "Germany",
    "France", "Brazil", "Mexico", "India", "Japan"
]


# Pre-generate content catalog for referencing
def generate_content_ids():
    return [f"CNT-{i:05d}" for i in range(1, 20001)]


CONTENT_IDS = generate_content_ids()
USER_IDS = [f"USR-{i:07d}" for i in range(1, 200001)]


# ---------------------------------------------------------------------------
# Genre-based title words for realistic titles
# ---------------------------------------------------------------------------

TITLE_WORDS_A = [
    "Dark", "Silent", "Burning", "Lost", "Broken", "Hidden", "Endless",
    "Forgotten", "Crimson", "Golden", "Shattered", "Midnight", "Final",
    "Eternal", "Rising", "Falling", "Deep", "Wild", "Electric", "Frozen"
]

TITLE_WORDS_B = [
    "Waters", "Roads", "Skies", "Hearts", "Minds", "Secrets", "Shadows",
    "Dreams", "Echoes", "Whispers", "Horizons", "Bridges", "Kingdoms",
    "Cities", "Tides", "Flames", "Winds", "Storms", "Memories", "Stars"
]


# ---------------------------------------------------------------------------
# 1. viewing-history.csv  (~80 MB, 500K records)
# ---------------------------------------------------------------------------

def generate_viewing_history():
    rng = random.Random(SEED_BASE + 1)
    outpath = os.path.join(SCRIPT_DIR, "viewing-history.csv")

    num_records = 700_000
    base_date = datetime(2025, 1, 1)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "user_id", "content_id", "start_time", "end_time",
            "duration_watched_min", "total_duration_min", "completion_pct",
            "device", "quality"
        ])

        for _ in range(num_records):
            uid = rng.choice(USER_IDS)
            cid = rng.choice(CONTENT_IDS)

            start = base_date + timedelta(
                days=rng.randint(0, 180),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59)
            )

            total_dur = rng.choices(
                [22, 30, 45, 52, 60, 90, 120, 150],
                weights=[10, 15, 15, 20, 10, 15, 10, 5],
                k=1
            )[0]

            # Completion: bimodal — many abandon early, many finish
            if rng.random() < 0.35:
                completion = rng.uniform(0.02, 0.30)
            elif rng.random() < 0.5:
                completion = rng.uniform(0.30, 0.80)
            else:
                completion = rng.uniform(0.80, 1.0)

            watched = round(total_dur * completion, 1)
            end = start + timedelta(minutes=int(watched) + rng.randint(0, 5))

            device = rng.choices(
                DEVICES, weights=[30, 25, 15, 20, 10], k=1
            )[0]

            quality = rng.choices(
                QUALITY_LEVELS, weights=[15, 55, 30], k=1
            )[0]

            writer.writerow([
                uid, cid,
                start.strftime("%Y-%m-%d %H:%M:%S"),
                end.strftime("%Y-%m-%d %H:%M:%S"),
                f"{watched:.1f}", total_dur,
                f"{completion * 100:.1f}",
                device, quality
            ])

    print(f"  viewing-history.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 2. content-catalog.json  (~5 MB, 20K records)
# ---------------------------------------------------------------------------

def generate_content_catalog():
    rng = random.Random(SEED_BASE + 2)
    outpath = os.path.join(SCRIPT_DIR, "content-catalog.json")

    records = []
    for i, cid in enumerate(CONTENT_IDS):
        title = f"{rng.choice(TITLE_WORDS_A)} {rng.choice(TITLE_WORDS_B)}"
        if rng.random() < 0.3:
            title += f" {rng.randint(2, 5)}"  # Sequel

        n_genres = rng.randint(1, 3)
        genres = rng.sample(GENRES, n_genres)

        release_year = rng.randint(1990, 2026)
        duration = rng.choices(
            [22, 30, 45, 52, 60, 90, 105, 120, 150],
            weights=[10, 10, 10, 15, 10, 20, 10, 10, 5],
            k=1
        )[0]

        rating = rng.choice(RATINGS)
        language = rng.choices(
            LANGUAGES,
            weights=[40, 10, 8, 8, 5, 5, 5, 7, 7, 5],
            k=1
        )[0]
        country = rng.choices(
            COUNTRIES,
            weights=[35, 10, 8, 7, 7, 5, 5, 5, 5, 4, 5, 4],
            k=1
        )[0]

        license_cost = round(rng.uniform(500, 150000), 2)
        imdb = round(max(1.0, min(10.0, rng.gauss(6.5, 1.5))), 1)

        is_series = rng.random() < 0.35
        seasons = rng.randint(1, 8) if is_series else None

        rec = {
            "content_id": cid,
            "title": title,
            "genre": genres,
            "release_year": release_year,
            "duration_min": duration,
            "rating": rating,
            "language": language,
            "country_origin": country,
            "license_cost_monthly": license_cost,
            "imdb_score": imdb
        }
        if seasons is not None:
            rec["seasons"] = seasons

        records.append(rec)

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  content-catalog.json: {len(records):,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 3. user-profiles.csv  (~30 MB, 200K records)
# ---------------------------------------------------------------------------

def generate_user_profiles():
    rng = random.Random(SEED_BASE + 3)
    outpath = os.path.join(SCRIPT_DIR, "user-profiles.csv")

    base_date = datetime(2020, 3, 1)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "user_id", "signup_date", "plan_type", "age_group", "country",
            "devices_registered", "monthly_hours_watched", "last_login",
            "is_churned"
        ])

        for uid in USER_IDS:
            signup = base_date + timedelta(days=rng.randint(0, 2000))
            plan = rng.choices(
                PLAN_TYPES, weights=[30, 45, 25], k=1
            )[0]
            age = rng.choice(AGE_GROUPS)
            country = rng.choices(
                USER_COUNTRIES,
                weights=[40, 10, 10, 5, 5, 5, 5, 5, 10, 5],
                k=1
            )[0]
            devices = rng.randint(1, 5)
            hours = round(max(0, rng.gauss(25, 15)), 1)

            # Churn: correlated with low hours
            if hours < 5:
                churned = rng.random() < 0.4
            elif hours < 15:
                churned = rng.random() < 0.15
            else:
                churned = rng.random() < 0.05

            if churned:
                last_login = signup + timedelta(
                    days=rng.randint(30, min(1800, (datetime(2026, 4, 1) - signup).days))
                )
            else:
                last_login = datetime(2026, 4, 1) - timedelta(
                    days=rng.randint(0, 14)
                )

            writer.writerow([
                uid, signup.strftime("%Y-%m-%d"), plan, age, country,
                devices, f"{hours:.1f}",
                last_login.strftime("%Y-%m-%d"), churned
            ])

    print(f"  user-profiles.csv: {len(USER_IDS):,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 4. user-interactions.json  (~65 MB, 400K records)
# ---------------------------------------------------------------------------

def generate_user_interactions():
    rng = random.Random(SEED_BASE + 4)
    outpath = os.path.join(SCRIPT_DIR, "user-interactions.json")

    num_records = 550_000
    base_date = datetime(2025, 1, 1)

    search_queries = [
        "action movies", "korean drama", "best documentaries", "new releases",
        "comedy series", "sci fi", "horror", "romantic comedy", "anime",
        "thriller", "true crime", "indie films", "family movies",
        "classic movies", "foreign language", "oscar winners", "top rated",
        "short films", "binge worthy", "cult classics"
    ]

    records = []
    for _ in range(num_records):
        uid = rng.choice(USER_IDS)
        ts = base_date + timedelta(
            days=rng.randint(0, 180),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
            seconds=rng.randint(0, 59)
        )

        action = rng.choices(
            USER_ACTIONS,
            weights=[25, 10, 30, 8, 7, 5, 10, 5],
            k=1
        )[0]

        rec = {
            "user_id": uid,
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
            "action": action,
            "content_id": rng.choice(CONTENT_IDS) if action != "search" else None,
        }

        if action == "search":
            rec["search_query"] = rng.choice(search_queries)
            rec["content_id"] = None
        else:
            rec["search_query"] = None

        if action == "rate":
            rec["rating_value"] = rng.randint(1, 5)
        else:
            rec["rating_value"] = None

        records.append(rec)

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  user-interactions.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 5. streaming-quality.csv  (~30 MB, 200K records)
# ---------------------------------------------------------------------------

def generate_streaming_quality():
    rng = random.Random(SEED_BASE + 5)
    outpath = os.path.join(SCRIPT_DIR, "streaming-quality.csv")

    num_records = 200_000
    base_date = datetime(2025, 1, 1)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "session_id", "user_id", "timestamp", "buffering_events",
            "avg_bitrate_mbps", "resolution_changes", "latency_ms",
            "cdn_region", "isp"
        ])

        for i in range(num_records):
            session_id = f"SES-{i + 1:08d}"
            uid = rng.choice(USER_IDS)
            ts = base_date + timedelta(
                days=rng.randint(0, 180),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59)
            )

            cdn = rng.choice(CDN_REGIONS)
            isp = rng.choice(ISPS)

            # Buffering: most sessions are fine, some are bad
            if rng.random() < 0.15:
                buffering = rng.randint(3, 15)  # Poor experience
            else:
                buffering = rng.randint(0, 2)

            bitrate = round(max(0.5, rng.gauss(8.0, 3.0)), 1)
            if buffering > 3:
                bitrate = round(max(0.5, bitrate * 0.5), 1)

            res_changes = rng.randint(0, 5) if buffering > 1 else rng.randint(0, 2)
            latency = int(max(10, rng.gauss(45, 20)))
            if buffering > 3:
                latency = int(max(10, rng.gauss(120, 50)))

            writer.writerow([
                session_id, uid, ts.strftime("%Y-%m-%d %H:%M:%S"),
                buffering, bitrate, res_changes, latency, cdn, isp
            ])

    print(f"  streaming-quality.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating MediaWave Streaming datasets (seed base=2091)...")
    generate_viewing_history()
    generate_content_catalog()
    generate_user_profiles()
    generate_user_interactions()
    generate_streaming_quality()
    print("Done.")
