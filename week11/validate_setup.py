#!/usr/bin/env python3
"""
validate_setup.py — Week 11 Airflow lab health check.

Run this from the lab directory AFTER `docker compose up -d` has finished
spinning up. It checks that:
  - all expected containers are running and healthy
  - the airflow-init one-shot completed successfully
  - host-side bind-mount folders exist
  - the Airflow Web UI is responding on http://localhost:8080
  - the Spark master UI is responding on http://localhost:8081
  - bind-mounts (dags/, scripts/, data/) are visible inside the
    airflow-scheduler container at /opt/airflow/<name>
  - DAGs in dags/ parse without import errors

No third-party Python packages required — just the standard library + the
docker CLI on your PATH.

Usage (from this directory):
    python validate_setup.py

Exits 0 on all-pass, 1 if any check fails.
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

# ─── Output helpers ───────────────────────────────────────────────
USE_COLOR = sys.stdout.isatty()
GREEN  = "\033[92m" if USE_COLOR else ""
RED    = "\033[91m" if USE_COLOR else ""
YELLOW = "\033[93m" if USE_COLOR else ""
BOLD   = "\033[1m"  if USE_COLOR else ""
RESET  = "\033[0m"  if USE_COLOR else ""

results = []

def check(name, ok, detail=""):
    icon = f"{GREEN}OK  {RESET}" if ok else f"{RED}FAIL{RESET}"
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{icon}] {name}{suffix}")
    results.append((name, ok, detail))
    return ok

def section(title):
    print(f"\n{BOLD}{YELLOW}{title}{RESET}")

def run(cmd, timeout=15):
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError:
        return -2, "", f"command not found: {cmd[0]}"

# ─── Section 1: Host-side bind-mount folders ──────────────────────
section("Host-side bind-mount folders (in this directory):")
for p in ("dags", "scripts", "data"):
    check(f"./{p}/ exists", os.path.isdir(p))

# ─── Section 2: docker CLI is reachable ───────────────────────────
section("Docker engine reachable:")
rc, out, err = run(["docker", "info"])
if not check("`docker info` succeeded", rc == 0,
             "is OrbStack/Docker Desktop running?" if rc != 0 else ""):
    print(f"\n{RED}Cannot reach the Docker engine. "
          f"Start OrbStack/Docker Desktop and re-run this script.{RESET}")
    sys.exit(1)

# ─── Section 3: Container status ──────────────────────────────────
section("Container status:")

# `docker compose ps -a --format json` outputs one JSON object per line.
rc, out, err = run(["docker", "compose", "ps", "-a", "--format", "json"])
if rc != 0:
    check("`docker compose ps`", False, f"exit code {rc}: {err}")
    print(f"\n{RED}Are you running this from the week11 lab directory?{RESET}")
    sys.exit(1)

containers = {}
for line in out.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except json.JSONDecodeError:
        continue
    # Match by container name (set in compose). Fall back to service name.
    key = d.get("Name") or d.get("Service")
    containers[key] = d

# Long-running services we expect "running"
long_running = [
    "airflow-postgres",
    "airflow-webserver",
    "airflow-scheduler",
    "spark-master",
    "spark-worker",
]
for name in long_running:
    info = containers.get(name)
    if info is None:
        check(f"{name} present", False, "not found in `docker compose ps -a`")
        continue
    state  = info.get("State", "?")
    health = info.get("Health", "")
    ok = state == "running" and health in ("healthy", "", "starting")
    detail_bits = [f"state={state}"]
    if health:
        detail_bits.append(f"health={health}")
    check(name, ok, ", ".join(detail_bits))

# airflow-init is a one-shot job — should be exited(0)
info = containers.get("airflow-init")
if info is None:
    check("airflow-init ran", False, "container not found")
else:
    state = info.get("State", "?")
    rc_code = info.get("ExitCode")
    ok = state == "exited" and (rc_code in (0, "0", None))
    check("airflow-init completed successfully",
          ok, f"state={state}, exit_code={rc_code}")

# ─── Section 4: Airflow Web UI ────────────────────────────────────
section("Airflow Web UI (http://localhost:8080):")
try:
    with urllib.request.urlopen("http://localhost:8080/health", timeout=5) as resp:
        body = resp.read().decode("utf-8")
        check("/health endpoint reachable", resp.status == 200,
              f"HTTP {resp.status}")
        try:
            data = json.loads(body)
            mdb = data.get("metadatabase", {}).get("status", "?")
            sch = data.get("scheduler",   {}).get("status", "?")
            check("metadatabase healthy", mdb == "healthy", f"status={mdb}")
            check("scheduler healthy",    sch == "healthy", f"status={sch}")
        except (json.JSONDecodeError, AttributeError) as e:
            check("/health body is JSON", False, str(e))
except urllib.error.URLError as e:
    check("/health endpoint reachable", False, f"unreachable: {e.reason}")

# ─── Section 5: Spark Master UI ───────────────────────────────────
section("Spark master UI (http://localhost:8081):")
try:
    with urllib.request.urlopen("http://localhost:8081/", timeout=5) as resp:
        check("Spark master UI reachable", resp.status == 200,
              f"HTTP {resp.status}")
except urllib.error.URLError as e:
    check("Spark master UI reachable", False, f"unreachable: {e.reason}")

# ─── Section 6: Bind-mounts visible inside scheduler ──────────────
section("Bind-mounts visible inside airflow-scheduler:")
for path in ("/opt/airflow/dags", "/opt/airflow/scripts", "/opt/airflow/data"):
    rc, _, _ = run(["docker", "exec", "airflow-scheduler", "test", "-d", path])
    check(path, rc == 0)

# ─── Section 7: DAG parse errors ──────────────────────────────────
section("DAG parse errors:")
rc, out, err = run(
    ["docker", "exec", "airflow-scheduler",
     "airflow", "dags", "list-import-errors"],
    timeout=30,
)
if rc != 0:
    check("`airflow dags list-import-errors` ran", False,
          f"exit code {rc}: {err.splitlines()[0] if err else ''}")
else:
    # Empty result: header line + "No data found" or just no rows after header
    lower = out.lower()
    no_errors = "no data found" in lower or out.strip() == "" \
                or out.strip().startswith("filepath")
    if no_errors and "traceback" not in lower:
        check("No DAG import errors", True)
    else:
        check("No DAG import errors", False)
        print(f"\n{RED}--- airflow dags list-import-errors output: ---{RESET}")
        print(out)
        print(f"{RED}--- end ---{RESET}")

# ─── Summary ──────────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for _, ok, _ in results if ok)
failed = total - passed

print()
if failed == 0:
    print(f"{BOLD}{GREEN}All {total} checks passed. The cluster is ready.{RESET}")
    print(f"  - Airflow UI : http://localhost:8080  (admin / admin)")
    print(f"  - Spark UI   : http://localhost:8081\n")
    sys.exit(0)
else:
    print(f"{BOLD}{RED}{failed} of {total} checks failed.{RESET}")
    print(f"\nCommon next steps:")
    print(f"  - Containers may still be starting; wait ~30s and re-run.")
    print(f"  - Inspect a service's logs:    docker compose logs <service>")
    print(f"  - List parse errors directly:  docker exec airflow-scheduler "
          f"airflow dags list-import-errors")
    print(f"  - Tear down + restart fresh:   docker compose down -v && "
          f"docker compose up -d\n")
    sys.exit(1)
