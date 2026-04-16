#!/usr/bin/env python3
"""
Generate synthetic datasets for Sportlytics Athletics (Project 07).
Seed base: 2061. Target total: ~155 MB.

Usage: python3 generate_data.py
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_BASE = 2061


# ---------------------------------------------------------------------------
# Shared reference data
# ---------------------------------------------------------------------------

TEAMS = [f"TEAM-{i:02d}" for i in range(1, 31)]

TEAM_CITIES = [
    "Atlanta", "Boston", "Brooklyn", "Charlotte", "Chicago", "Cleveland",
    "Dallas", "Denver", "Detroit", "Golden State", "Houston", "Indiana",
    "LA Clippers", "LA Lakers", "Memphis", "Miami", "Milwaukee", "Minnesota",
    "New Orleans", "New York", "OKC", "Orlando", "Philadelphia", "Phoenix",
    "Portland", "Sacramento", "San Antonio", "Toronto", "Utah", "Washington"
]

VENUES = [f"{city} Arena" for city in TEAM_CITIES]

# 15 players per team = 450 players
PLAYER_IDS = [f"PLR-{i:04d}" for i in range(1, 451)]

POSITIONS = ["PG", "SG", "SF", "PF", "C"]

INJURY_TYPES = ["ankle", "knee", "hamstring", "shoulder", "concussion", "back"]
INJURY_SEVERITIES = ["minor", "moderate", "severe"]

SESSION_TYPES = ["practice", "gym", "recovery", "film"]

TREATMENTS = [
    "rest", "physical_therapy", "ice_compression", "surgery",
    "rehabilitation", "cortisone_injection", "taping_brace"
]


def assign_players_to_teams(rng):
    """Assign 15 players per team."""
    assignments = {}
    pids = list(PLAYER_IDS)
    rng.shuffle(pids)
    for i, team in enumerate(TEAMS):
        assignments[team] = pids[i * 15:(i + 1) * 15]
    return assignments


# ---------------------------------------------------------------------------
# 1. player-tracking.csv  (~85 MB, 500K records)
# ---------------------------------------------------------------------------

def generate_player_tracking():
    rng = random.Random(SEED_BASE + 1)
    outpath = os.path.join(SCRIPT_DIR, "player-tracking.csv")

    team_players = assign_players_to_teams(rng)
    game_ids = [f"GAME-{i:05d}" for i in range(1, 2001)]
    num_records = 750_000

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "game_id", "player_id", "timestamp", "x_court_ft", "y_court_ft",
            "speed_mph", "acceleration", "distance_covered_ft",
            "heart_rate_bpm", "team_id"
        ])

        base_date = datetime(2025, 10, 15)

        for _ in range(num_records):
            game_id = rng.choice(game_ids)
            team_id = rng.choice(TEAMS)
            player_id = rng.choice(team_players[team_id])

            ts = base_date + timedelta(
                days=rng.randint(0, 180),
                hours=rng.choice([19, 20, 21]),
                minutes=rng.randint(0, 59),
                seconds=rng.randint(0, 59)
            )

            x = round(rng.uniform(0, 94), 1)   # Court is 94 ft long
            y = round(rng.uniform(0, 50), 1)    # Court is 50 ft wide
            speed = round(max(0, rng.gauss(8.0, 4.0)), 1)
            accel = round(rng.gauss(0.0, 3.0), 2)
            dist = round(rng.uniform(0, 500), 1)
            hr = int(max(60, min(220, rng.gauss(145, 25))))

            writer.writerow([
                game_id, player_id, ts.strftime("%Y-%m-%d %H:%M:%S"),
                x, y, speed, accel, dist, hr, team_id
            ])

    print(f"  player-tracking.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 2. game-stats.json  (~40 MB, 200K records)
# ---------------------------------------------------------------------------

def generate_game_stats():
    rng = random.Random(SEED_BASE + 2)
    outpath = os.path.join(SCRIPT_DIR, "game-stats.json")

    team_players = assign_players_to_teams(rng)
    game_ids = [f"GAME-{i:05d}" for i in range(1, 2001)]
    quarters = [1, 2, 3, 4]
    num_records = 300_000

    records = []
    for _ in range(num_records):
        game_id = rng.choice(game_ids)
        team_id = rng.choice(TEAMS)
        player_id = rng.choice(team_players[team_id])
        quarter = rng.choice(quarters)

        minutes = round(rng.uniform(2, 12), 1)
        shot_att = rng.randint(0, 12)
        shot_made = rng.randint(0, shot_att)
        three_att = rng.randint(0, max(1, shot_att // 2))
        three_made = rng.randint(0, three_att)
        ft_att = rng.randint(0, 6)
        ft_made = rng.randint(0, ft_att)
        points = shot_made * 2 + three_made + ft_made

        records.append({
            "game_id": game_id,
            "player_id": player_id,
            "quarter": quarter,
            "points": points,
            "rebounds": rng.randint(0, 6),
            "assists": rng.randint(0, 5),
            "steals": rng.randint(0, 3),
            "blocks": rng.randint(0, 2),
            "turnovers": rng.randint(0, 3),
            "fouls": rng.randint(0, 3),
            "minutes_played": minutes,
            "plus_minus": rng.randint(-15, 15),
            "shot_attempts": shot_att,
            "shot_made": shot_made,
            "three_pt_attempts": three_att,
            "three_pt_made": three_made
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  game-stats.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 3. injury-reports.csv  (~3 MB, 15K records)
# ---------------------------------------------------------------------------

def generate_injury_reports():
    rng = random.Random(SEED_BASE + 3)
    outpath = os.path.join(SCRIPT_DIR, "injury-reports.csv")

    num_records = 15_000
    base_date = datetime(2021, 10, 1)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "player_id", "date", "injury_type", "severity",
            "games_missed", "treatment", "return_date"
        ])

        for _ in range(num_records):
            pid = rng.choice(PLAYER_IDS)
            injury_date = base_date + timedelta(days=rng.randint(0, 1500))
            itype = rng.choice(INJURY_TYPES)
            severity = rng.choices(
                INJURY_SEVERITIES, weights=[50, 35, 15], k=1
            )[0]

            if severity == "minor":
                games = rng.randint(0, 5)
            elif severity == "moderate":
                games = rng.randint(3, 20)
            else:
                games = rng.randint(15, 60)

            treatment = rng.choice(TREATMENTS)
            return_date = injury_date + timedelta(days=games * 2 + rng.randint(1, 7))

            writer.writerow([
                pid, injury_date.strftime("%Y-%m-%d"), itype, severity,
                games, treatment, return_date.strftime("%Y-%m-%d")
            ])

    print(f"  injury-reports.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 4. training-sessions.json  (~25 MB, 150K records)
# ---------------------------------------------------------------------------

def generate_training_sessions():
    rng = random.Random(SEED_BASE + 4)
    outpath = os.path.join(SCRIPT_DIR, "training-sessions.json")

    num_records = 150_000
    base_date = datetime(2025, 9, 15)

    records = []
    for _ in range(num_records):
        pid = rng.choice(PLAYER_IDS)
        session_date = base_date + timedelta(days=rng.randint(0, 210))
        stype = rng.choices(
            SESSION_TYPES, weights=[35, 25, 25, 15], k=1
        )[0]

        if stype == "practice":
            duration = rng.randint(60, 150)
            intensity = rng.randint(5, 10)
        elif stype == "gym":
            duration = rng.randint(30, 90)
            intensity = rng.randint(4, 9)
        elif stype == "recovery":
            duration = rng.randint(20, 60)
            intensity = rng.randint(1, 4)
        else:  # film
            duration = rng.randint(30, 90)
            intensity = rng.randint(1, 3)

        hr_avg = int(max(60, min(200, rng.gauss(120, 20) * (intensity / 7))))
        hr_max = hr_avg + rng.randint(10, 40)
        hr_max = min(220, hr_max)
        calories = int(duration * intensity * rng.uniform(0.8, 1.5))
        sleep = round(max(3, min(12, rng.gauss(7.2, 1.3))), 1)

        records.append({
            "player_id": pid,
            "date": session_date.strftime("%Y-%m-%d"),
            "session_type": stype,
            "duration_min": duration,
            "intensity_score": intensity,
            "heart_rate_avg": hr_avg,
            "heart_rate_max": hr_max,
            "calories_burned": calories,
            "sleep_hours_prev_night": sleep
        })

    with open(outpath, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"  training-sessions.json: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# 5. team-schedules.csv  (~2 MB, 10K records)
# ---------------------------------------------------------------------------

def generate_team_schedules():
    rng = random.Random(SEED_BASE + 5)
    outpath = os.path.join(SCRIPT_DIR, "team-schedules.csv")

    num_records = 10_000
    game_ids = [f"GAME-{i:05d}" for i in range(1, num_records + 1)]
    base_date = datetime(2021, 10, 19)

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "game_id", "date", "home_team", "away_team", "venue",
            "travel_distance_miles", "rest_days_since_last_game",
            "back_to_back", "result", "score_home", "score_away"
        ])

        for i in range(num_records):
            gid = game_ids[i]
            game_date = base_date + timedelta(days=rng.randint(0, 1500))
            home_idx = rng.randint(0, 29)
            away_idx = rng.randint(0, 29)
            while away_idx == home_idx:
                away_idx = rng.randint(0, 29)

            home_team = TEAMS[home_idx]
            away_team = TEAMS[away_idx]
            venue = VENUES[home_idx]
            travel = rng.randint(0, 2800)
            rest_days = rng.choices(
                [0, 1, 2, 3, 4, 5], weights=[15, 35, 25, 15, 7, 3], k=1
            )[0]
            b2b = rest_days == 0

            score_home = rng.randint(85, 135)
            score_away = rng.randint(85, 135)
            result = "W" if score_home > score_away else "L"

            writer.writerow([
                gid, game_date.strftime("%Y-%m-%d"), home_team, away_team,
                venue, travel, rest_days, b2b, result, score_home, score_away
            ])

    print(f"  team-schedules.csv: {num_records:,} records "
          f"({os.path.getsize(outpath) / 1e6:.1f} MB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating Sportlytics Athletics datasets (seed base=2061)...")
    generate_player_tracking()
    generate_game_stats()
    generate_injury_reports()
    generate_training_sessions()
    generate_team_schedules()
    print("Done.")
