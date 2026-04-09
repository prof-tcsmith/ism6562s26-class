#!/usr/bin/env python3
"""
ETL Pipeline: Operational Databases → Data Warehouse
ISM 6562 - Week 03 Assignment

This script extracts data from two operational databases (Sales and HR),
transforms it into a star schema format, and loads it into a data warehouse.

Phases:
  1. EXTRACT  - Read rows from sales-db and hr-db
  2. TRANSFORM - Generate dim_date; denormalize employee + department
  3. LOAD      - Upsert dimensions and insert facts (idempotent)
"""

import os
import sys
from datetime import date, timedelta

import psycopg2
from psycopg2.extras import execute_values


# ---------------------------------------------------------------------------
# Database connection helpers
# ---------------------------------------------------------------------------

def get_connection(prefix):
    """Create a database connection using environment variables."""
    return psycopg2.connect(
        host=os.environ[f"{prefix}_DB_HOST"],
        port=os.environ[f"{prefix}_DB_PORT"],
        dbname=os.environ[f"{prefix}_DB_NAME"],
        user=os.environ[f"{prefix}_DB_USER"],
        password=os.environ[f"{prefix}_DB_PASSWORD"],
    )


# ---------------------------------------------------------------------------
# EXTRACT phase
# ---------------------------------------------------------------------------

def extract_sales(conn):
    """Extract customers, products, and orders from the sales database."""
    cur = conn.cursor()

    cur.execute("SELECT customer_id, first_name, last_name, email, city, state FROM customers;")
    customers = cur.fetchall()
    print(f"  Extracted {len(customers)} customers from sales-db")

    cur.execute("SELECT product_id, product_name, category, unit_price FROM products;")
    products = cur.fetchall()
    print(f"  Extracted {len(products)} products from sales-db")

    cur.execute("""
        SELECT order_id, customer_id, product_id, quantity, total_price, order_date
        FROM orders;
    """)
    orders = cur.fetchall()
    print(f"  Extracted {len(orders)} orders from sales-db")

    cur.close()
    return customers, products, orders


def extract_hr(conn):
    """Extract employees joined with departments from the HR database."""
    cur = conn.cursor()

    cur.execute("""
        SELECT e.employee_id, e.first_name, e.last_name, e.email,
               e.job_title, d.department_name, d.location
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id;
    """)
    employees = cur.fetchall()
    print(f"  Extracted {len(employees)} employees from hr-db")

    cur.close()
    return employees


# ---------------------------------------------------------------------------
# TRANSFORM phase
# ---------------------------------------------------------------------------

def generate_dim_date_rows(year):
    """Generate one row per day for the given year."""
    rows = []
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    current = date(year, 1, 1)
    end = date(year, 12, 31)

    while current <= end:
        date_key = int(current.strftime("%Y%m%d"))
        rows.append((
            date_key,
            current,
            current.year,
            (current.month - 1) // 3 + 1,  # quarter
            current.month,
            month_names[current.month - 1],
            current.day,
            current.weekday(),              # 0=Monday
            day_names[current.weekday()],
            current.weekday() >= 5,         # is_weekend
        ))
        current += timedelta(days=1)

    print(f"  Generated {len(rows)} dim_date rows for {year}")
    return rows


# ---------------------------------------------------------------------------
# LOAD phase
# ---------------------------------------------------------------------------

def load_dim_date(cur, rows):
    """Load date dimension (insert, skip conflicts)."""
    execute_values(cur, """
        INSERT INTO dim_date (date_key, full_date, year, quarter, month,
                              month_name, day_of_month, day_of_week, day_name, is_weekend)
        VALUES %s
        ON CONFLICT (date_key) DO NOTHING;
    """, rows)
    print(f"  Loaded dim_date ({len(rows)} rows, conflicts skipped)")


def load_dim_customer(cur, customers):
    """Load customer dimension (upsert on source_customer_id)."""
    rows = [(c[0], c[1], c[2], c[3], c[4], c[5]) for c in customers]
    execute_values(cur, """
        INSERT INTO dim_customer (source_customer_id, first_name, last_name, email, city, state)
        VALUES %s
        ON CONFLICT (source_customer_id) DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name  = EXCLUDED.last_name,
            email      = EXCLUDED.email,
            city       = EXCLUDED.city,
            state      = EXCLUDED.state;
    """, rows)
    print(f"  Loaded dim_customer ({len(rows)} rows, upserted)")


def load_dim_product(cur, products):
    """Load product dimension (upsert on source_product_id)."""
    rows = [(p[0], p[1], p[2], p[3]) for p in products]
    execute_values(cur, """
        INSERT INTO dim_product (source_product_id, product_name, category, unit_price)
        VALUES %s
        ON CONFLICT (source_product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category     = EXCLUDED.category,
            unit_price   = EXCLUDED.unit_price;
    """, rows)
    print(f"  Loaded dim_product ({len(rows)} rows, upserted)")


def load_dim_employee(cur, employees):
    """Load employee dimension with denormalized department info."""
    rows = [(e[0], e[1], e[2], e[3], e[4], e[5], e[6]) for e in employees]
    execute_values(cur, """
        INSERT INTO dim_employee (source_employee_id, first_name, last_name,
                                  email, job_title, department_name, department_location)
        VALUES %s
        ON CONFLICT (source_employee_id) DO UPDATE SET
            first_name          = EXCLUDED.first_name,
            last_name           = EXCLUDED.last_name,
            email               = EXCLUDED.email,
            job_title           = EXCLUDED.job_title,
            department_name     = EXCLUDED.department_name,
            department_location = EXCLUDED.department_location;
    """, rows)
    print(f"  Loaded dim_employee ({len(rows)} rows, upserted)")


def load_fact_sales(cur, orders):
    """Load fact_sales by looking up surrogate keys from dimensions."""
    inserted = 0
    skipped = 0

    for order in orders:
        order_id, customer_id, product_id, quantity, total_price, order_date = order
        date_key = int(order_date.strftime("%Y%m%d"))

        # Look up surrogate keys
        cur.execute("SELECT customer_key FROM dim_customer WHERE source_customer_id = %s;",
                    (customer_id,))
        cust_row = cur.fetchone()

        cur.execute("SELECT product_key FROM dim_product WHERE source_product_id = %s;",
                    (product_id,))
        prod_row = cur.fetchone()

        cur.execute("SELECT unit_price FROM dim_product WHERE source_product_id = %s;",
                    (product_id,))
        price_row = cur.fetchone()

        if cust_row and prod_row and price_row:
            cur.execute("""
                INSERT INTO fact_sales (date_key, customer_key, product_key,
                                        source_order_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_order_id) DO NOTHING;
            """, (date_key, cust_row[0], prod_row[0],
                  order_id, quantity, price_row[0], total_price))
            if cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        else:
            print(f"  WARNING: Could not find dimension keys for order {order_id}")

    print(f"  Loaded fact_sales ({inserted} inserted, {skipped} already existed)")


# ---------------------------------------------------------------------------
# Main ETL orchestrator
# ---------------------------------------------------------------------------

def run_etl():
    """Execute the full ETL pipeline."""
    print("=" * 60)
    print("ETL Pipeline Starting")
    print("=" * 60)

    # --- EXTRACT ---
    print("\n[EXTRACT] Reading from operational databases...")
    sales_conn = get_connection("SALES")
    customers, products, orders = extract_sales(sales_conn)
    sales_conn.close()

    hr_conn = get_connection("HR")
    employees = extract_hr(hr_conn)
    hr_conn.close()

    # --- TRANSFORM ---
    print("\n[TRANSFORM] Preparing dimension data...")
    dim_date_rows = generate_dim_date_rows(2026)
    print("  Employee dimension: denormalized with department info (done in extract query)")

    # --- LOAD ---
    print("\n[LOAD] Writing to data warehouse...")
    wh_conn = get_connection("WAREHOUSE")
    cur = wh_conn.cursor()

    load_dim_date(cur, dim_date_rows)
    load_dim_customer(cur, customers)
    load_dim_product(cur, products)
    load_dim_employee(cur, employees)
    load_fact_sales(cur, orders)

    wh_conn.commit()
    cur.close()
    wh_conn.close()

    print("\n" + "=" * 60)
    print("ETL Pipeline Complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_etl()
    except Exception as e:
        print(f"ETL FAILED: {e}", file=sys.stderr)
        sys.exit(1)
