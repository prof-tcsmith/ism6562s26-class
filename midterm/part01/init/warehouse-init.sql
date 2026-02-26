-- Data Warehouse Database (Star Schema)
-- ISM 6562 - Week 03 Assignment
--
-- Star schema with 4 dimension tables and 1 fact table.
-- Tables are created empty; the ETL service populates them.

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE dim_date (
    date_key     INTEGER PRIMARY KEY,       -- YYYYMMDD format
    full_date    DATE NOT NULL UNIQUE,
    year         INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    month_name   VARCHAR(20) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week  INTEGER NOT NULL,           -- 0=Monday, 6=Sunday
    day_name     VARCHAR(20) NOT NULL,
    is_weekend   BOOLEAN NOT NULL
);

CREATE TABLE dim_customer (
    customer_key       SERIAL PRIMARY KEY,
    source_customer_id INTEGER UNIQUE NOT NULL,
    first_name         VARCHAR(100) NOT NULL,
    last_name          VARCHAR(100) NOT NULL,
    email              VARCHAR(255) NOT NULL,
    city               VARCHAR(100),
    state              VARCHAR(2)
);

CREATE TABLE dim_product (
    product_key       SERIAL PRIMARY KEY,
    source_product_id INTEGER UNIQUE NOT NULL,
    product_name      VARCHAR(200) NOT NULL,
    category          VARCHAR(100) NOT NULL,
    unit_price        NUMERIC(10,2) NOT NULL
);

CREATE TABLE dim_employee (
    employee_key        SERIAL PRIMARY KEY,
    source_employee_id  INTEGER UNIQUE NOT NULL,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255) NOT NULL,
    job_title           VARCHAR(100) NOT NULL,
    department_name     VARCHAR(100) NOT NULL,    -- denormalized from departments
    department_location VARCHAR(100) NOT NULL      -- denormalized from departments
);

-- ============================================================
-- FACT TABLE
-- ============================================================

CREATE TABLE fact_sales (
    sale_key        SERIAL PRIMARY KEY,
    date_key        INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key    INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key     INTEGER NOT NULL REFERENCES dim_product(product_key),
    source_order_id INTEGER UNIQUE NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(10,2) NOT NULL,
    total_price     NUMERIC(10,2) NOT NULL
);

-- ============================================================
-- INDEXES ON FACT TABLE FOREIGN KEYS
-- ============================================================

CREATE INDEX idx_fact_sales_date_key     ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer_key ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product_key  ON fact_sales(product_key);
