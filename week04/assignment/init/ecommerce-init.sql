-- Week 04: E-Commerce Database for Partitioning Assignment
-- ISM 6562 - Big Data for Business Applications
--
-- Schema: customers → orders ← products
-- 1,000 customers, 200 products, 500,000 orders
-- Date range: Jan 1, 2024 to Mar 31, 2026 (~27 months)
-- No indexes on orders beyond PK (students will create partitioned tables)

-- ============================================================
-- Customers Table (1,000 rows)
-- 4 regions: Northeast, Southeast, Midwest, West
-- ============================================================
CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) NOT NULL,
    region        VARCHAR(20)  NOT NULL CHECK (region IN ('Northeast', 'Southeast', 'Midwest', 'West'))
);

INSERT INTO customers (first_name, last_name, email, region)
SELECT
    'Customer' || g,
    'Last' || g,
    'customer' || g || '@example.com',
    CASE (g % 4)
        WHEN 0 THEN 'Northeast'
        WHEN 1 THEN 'Southeast'
        WHEN 2 THEN 'Midwest'
        WHEN 3 THEN 'West'
    END
FROM generate_series(1, 1000) AS g;

-- ============================================================
-- Products Table (200 rows)
-- 5 categories: Electronics, Clothing, Home, Sports, Books
-- ============================================================
CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    category     VARCHAR(20)  NOT NULL CHECK (category IN ('Electronics', 'Clothing', 'Home', 'Sports', 'Books')),
    price        NUMERIC(10, 2) NOT NULL
);

INSERT INTO products (name, category, price)
SELECT
    CASE ((g - 1) % 5)
        WHEN 0 THEN 'Electronic Device '
        WHEN 1 THEN 'Clothing Item '
        WHEN 2 THEN 'Home Product '
        WHEN 3 THEN 'Sports Gear '
        WHEN 4 THEN 'Book Title '
    END || g,
    CASE ((g - 1) % 5)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Clothing'
        WHEN 2 THEN 'Home'
        WHEN 3 THEN 'Sports'
        WHEN 4 THEN 'Books'
    END,
    ROUND((10.0 + random() * 490.0)::numeric, 2)
FROM generate_series(1, 200) AS g;

-- ============================================================
-- Orders Table (500,000 rows)
-- Date range: Jan 1, 2024 to Mar 31, 2026 (~27 months)
-- ~18,500 orders per month
-- NO indexes beyond PK (students will create partitioned tables)
-- ============================================================
CREATE TABLE orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   INTEGER        NOT NULL REFERENCES customers(customer_id),
    product_id    INTEGER        NOT NULL REFERENCES products(product_id),
    order_date    DATE           NOT NULL,
    quantity      INTEGER        NOT NULL,
    total_amount  NUMERIC(10, 2) NOT NULL,
    status        VARCHAR(20)    NOT NULL CHECK (status IN ('pending', 'shipped', 'delivered', 'returned'))
);

INSERT INTO orders (customer_id, product_id, order_date, quantity, total_amount, status)
SELECT
    (floor(random() * 1000) + 1)::int,
    (floor(random() * 200) + 1)::int,
    ('2024-01-01'::date + (random() * 820)::int),
    (floor(random() * 5) + 1)::int,
    ROUND((10.0 + random() * 990.0)::numeric, 2),
    CASE (floor(random() * 4))::int
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'shipped'
        WHEN 2 THEN 'delivered'
        WHEN 3 THEN 'returned'
    END
FROM generate_series(1, 500000);

-- ============================================================
-- Verify counts
-- ============================================================
DO $$
DECLARE
    cust_count    INTEGER;
    prod_count    INTEGER;
    order_count   INTEGER;
    min_date      DATE;
    max_date      DATE;
BEGIN
    SELECT COUNT(*) INTO cust_count  FROM customers;
    SELECT COUNT(*) INTO prod_count  FROM products;
    SELECT COUNT(*) INTO order_count FROM orders;
    SELECT MIN(order_date), MAX(order_date) INTO min_date, max_date FROM orders;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Data loaded successfully:';
    RAISE NOTICE '  Customers:   %', cust_count;
    RAISE NOTICE '  Products:    %', prod_count;
    RAISE NOTICE '  Orders:      %', order_count;
    RAISE NOTICE '  Date range:  % to %', min_date, max_date;
    RAISE NOTICE '========================================';
END $$;
