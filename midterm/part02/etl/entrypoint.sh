#!/bin/bash

echo "=== ETL Service Starting ==="
echo "Running initial ETL load..."

# Pass environment variables to cron
printenv | grep -E '^(SALES_|HR_|WAREHOUSE_)' >> /etc/environment

# Run ETL immediately on startup (may fail if script needs updating)
python /app/etl_script.py || echo "WARNING: Initial ETL run failed. Check the script and try again."

echo ""
echo "Starting cron for scheduled runs (every 5 minutes)..."

# Start cron in the foreground
cron -f
