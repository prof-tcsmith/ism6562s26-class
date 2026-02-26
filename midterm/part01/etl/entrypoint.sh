#!/bin/bash
set -e

echo "=== ETL Service Starting ==="
echo "Running initial ETL load..."

# Pass environment variables to cron
printenv | grep -E '^(SALES_|HR_|WAREHOUSE_)' >> /etc/environment

# Run ETL immediately on startup
python /app/etl_script.py

echo ""
echo "Initial ETL complete. Starting cron for scheduled runs (every 5 minutes)..."

# Start cron in the foreground
cron -f
