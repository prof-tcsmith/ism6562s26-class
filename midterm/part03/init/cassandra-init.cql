-- Cassandra Schema and Seed Data for TechRetail Order Ingestion
-- ISM 6562 - Midterm Part 3
--
-- Query-first design:
--   Table 1: orders_by_customer — "Get all orders for a customer" (order tracking)
--   Table 2: orders_by_product  — "Get all orders for a product" (sales monitoring)
--
-- All order data is denormalized: customer names/states and product names/categories
-- are embedded in each row to avoid JOINs (which Cassandra does not support).

-- ============================================================
-- KEYSPACE
-- ============================================================

CREATE KEYSPACE IF NOT EXISTS techretail_orders
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 2
};

USE techretail_orders;

-- ============================================================
-- TABLE 1: Orders by Customer (partition key = customer_id)
-- Query: "Get all orders for a given customer, most recent first"
-- ============================================================

CREATE TABLE IF NOT EXISTS orders_by_customer (
    customer_id      INT,
    order_date       DATE,
    order_id         INT,
    product_id       INT,
    product_name     TEXT,
    product_category TEXT,
    quantity         INT,
    unit_price       DECIMAL,
    total_price      DECIMAL,
    customer_name    TEXT,
    customer_state   TEXT,
    PRIMARY KEY ((customer_id), order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC, order_id DESC);

-- ============================================================
-- TABLE 2: Orders by Product (partition key = product_id)
-- Query: "Get all orders for a given product, most recent first"
-- ============================================================

CREATE TABLE IF NOT EXISTS orders_by_product (
    product_id    INT,
    order_date    DATE,
    order_id      INT,
    customer_id   INT,
    customer_name TEXT,
    quantity      INT,
    total_price   DECIMAL,
    PRIMARY KEY ((product_id), order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC, order_id DESC);

-- ============================================================
-- SEED DATA: orders_by_customer (all 27 orders, denormalized)
-- ============================================================

-- Customer 1: Alice Johnson, Tampa, FL (5 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (1, '2026-01-05', 1, 1, 'Laptop Pro 15', 'Electronics', 1, 1299.99, 1299.99, 'Alice Johnson', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (1, '2026-01-05', 2, 2, 'Wireless Mouse', 'Electronics', 2, 29.99, 59.98, 'Alice Johnson', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (1, '2026-01-18', 8, 10, 'Monitor 27-inch', 'Electronics', 1, 349.99, 349.99, 'Alice Johnson', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (1, '2026-02-03', 17, 5, 'Ergonomic Chair', 'Furniture', 1, 449.99, 449.99, 'Alice Johnson', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (1, '2026-02-18', 25, 3, 'USB-C Hub', 'Electronics', 1, 49.99, 49.99, 'Alice Johnson', 'FL');

-- Customer 2: Bob Smith, Orlando, FL (4 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (2, '2026-01-08', 3, 4, 'Standing Desk', 'Furniture', 1, 599.99, 599.99, 'Bob Smith', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (2, '2026-01-12', 5, 3, 'USB-C Hub', 'Electronics', 1, 49.99, 49.99, 'Bob Smith', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (2, '2026-01-30', 15, 10, 'Monitor 27-inch', 'Electronics', 1, 349.99, 349.99, 'Bob Smith', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (2, '2026-02-12', 22, 7, 'Python Cookbook', 'Books', 2, 45.99, 91.98, 'Bob Smith', 'FL');

-- Customer 3: Carol Williams, Atlanta, GA (4 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (3, '2026-01-10', 4, 7, 'Python Cookbook', 'Books', 3, 45.99, 137.97, 'Carol Williams', 'GA');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (3, '2026-01-22', 10, 1, 'Laptop Pro 15', 'Electronics', 1, 1299.99, 1299.99, 'Carol Williams', 'GA');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (3, '2026-02-05', 18, 3, 'USB-C Hub', 'Electronics', 2, 49.99, 99.98, 'Carol Williams', 'GA');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (3, '2026-02-20', 26, 9, 'Noise-Cancel Headset', 'Electronics', 1, 199.99, 199.99, 'Carol Williams', 'GA');

-- Customer 4: David Brown, Miami, FL (3 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (4, '2026-01-14', 6, 5, 'Ergonomic Chair', 'Furniture', 1, 449.99, 449.99, 'David Brown', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (4, '2026-01-25', 12, 2, 'Wireless Mouse', 'Electronics', 3, 29.99, 89.97, 'David Brown', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (4, '2026-02-08', 20, 9, 'Noise-Cancel Headset', 'Electronics', 1, 199.99, 199.99, 'David Brown', 'FL');

-- Customer 5: Eva Davis, Charlotte, NC (3 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (5, '2026-01-15', 7, 8, 'Data Engineering 101', 'Books', 2, 39.99, 79.98, 'Eva Davis', 'NC');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (5, '2026-01-28', 14, 4, 'Standing Desk', 'Furniture', 1, 599.99, 599.99, 'Eva Davis', 'NC');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (5, '2026-02-14', 23, 1, 'Laptop Pro 15', 'Electronics', 1, 1299.99, 1299.99, 'Eva Davis', 'NC');

-- Customer 6: Frank Miller, Jacksonville, FL (3 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (6, '2026-01-20', 9, 9, 'Noise-Cancel Headset', 'Electronics', 1, 199.99, 199.99, 'Frank Miller', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (6, '2026-02-01', 16, 1, 'Laptop Pro 15', 'Electronics', 1, 1299.99, 1299.99, 'Frank Miller', 'FL');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (6, '2026-02-16', 24, 5, 'Ergonomic Chair', 'Furniture', 1, 449.99, 449.99, 'Frank Miller', 'FL');

-- Customer 7: Grace Wilson, Nashville, TN (3 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (7, '2026-01-23', 11, 6, 'LED Desk Lamp', 'Furniture', 2, 79.99, 159.98, 'Grace Wilson', 'TN');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (7, '2026-02-06', 19, 8, 'Data Engineering 101', 'Books', 1, 39.99, 39.99, 'Grace Wilson', 'TN');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (7, '2026-02-22', 27, 10, 'Monitor 27-inch', 'Electronics', 1, 349.99, 349.99, 'Grace Wilson', 'TN');

-- Customer 8: Henry Taylor, Savannah, GA (2 orders)
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (8, '2026-01-26', 13, 7, 'Python Cookbook', 'Books', 1, 45.99, 45.99, 'Henry Taylor', 'GA');
INSERT INTO orders_by_customer (customer_id, order_date, order_id, product_id, product_name, product_category, quantity, unit_price, total_price, customer_name, customer_state)
VALUES (8, '2026-02-10', 21, 6, 'LED Desk Lamp', 'Furniture', 1, 79.99, 79.99, 'Henry Taylor', 'GA');

-- ============================================================
-- SEED DATA: orders_by_product (all 27 orders, denormalized)
-- ============================================================

-- Product 1: Laptop Pro 15 (4 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (1, '2026-01-05', 1, 1, 'Alice Johnson', 1, 1299.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (1, '2026-01-22', 10, 3, 'Carol Williams', 1, 1299.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (1, '2026-02-01', 16, 6, 'Frank Miller', 1, 1299.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (1, '2026-02-14', 23, 5, 'Eva Davis', 1, 1299.99);

-- Product 2: Wireless Mouse (2 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (2, '2026-01-05', 2, 1, 'Alice Johnson', 2, 59.98);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (2, '2026-01-25', 12, 4, 'David Brown', 3, 89.97);

-- Product 3: USB-C Hub (3 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (3, '2026-01-12', 5, 2, 'Bob Smith', 1, 49.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (3, '2026-02-05', 18, 3, 'Carol Williams', 2, 99.98);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (3, '2026-02-18', 25, 1, 'Alice Johnson', 1, 49.99);

-- Product 4: Standing Desk (2 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (4, '2026-01-08', 3, 2, 'Bob Smith', 1, 599.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (4, '2026-01-28', 14, 5, 'Eva Davis', 1, 599.99);

-- Product 5: Ergonomic Chair (3 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (5, '2026-01-14', 6, 4, 'David Brown', 1, 449.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (5, '2026-02-03', 17, 1, 'Alice Johnson', 1, 449.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (5, '2026-02-16', 24, 6, 'Frank Miller', 1, 449.99);

-- Product 6: LED Desk Lamp (2 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (6, '2026-01-23', 11, 7, 'Grace Wilson', 2, 159.98);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (6, '2026-02-10', 21, 8, 'Henry Taylor', 1, 79.99);

-- Product 7: Python Cookbook (3 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (7, '2026-01-10', 4, 3, 'Carol Williams', 3, 137.97);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (7, '2026-01-26', 13, 8, 'Henry Taylor', 1, 45.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (7, '2026-02-12', 22, 2, 'Bob Smith', 2, 91.98);

-- Product 8: Data Engineering 101 (2 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (8, '2026-01-15', 7, 5, 'Eva Davis', 2, 79.98);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (8, '2026-02-06', 19, 7, 'Grace Wilson', 1, 39.99);

-- Product 9: Noise-Cancel Headset (3 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (9, '2026-01-20', 9, 6, 'Frank Miller', 1, 199.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (9, '2026-02-08', 20, 4, 'David Brown', 1, 199.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (9, '2026-02-20', 26, 3, 'Carol Williams', 1, 199.99);

-- Product 10: Monitor 27-inch (3 orders)
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (10, '2026-01-18', 8, 1, 'Alice Johnson', 1, 349.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (10, '2026-01-30', 15, 2, 'Bob Smith', 1, 349.99);
INSERT INTO orders_by_product (product_id, order_date, order_id, customer_id, customer_name, quantity, total_price)
VALUES (10, '2026-02-22', 27, 7, 'Grace Wilson', 1, 349.99);
