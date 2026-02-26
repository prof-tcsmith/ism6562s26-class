-- Sales Shard: Southeast (FL, GA, TN)
-- ISM 6562 - Midterm Part 2
--
-- This shard contains customers located in Florida, Georgia, and Tennessee.
-- 7 customers, ~24 orders, all 10 products (reference table).

-- ============================================================
-- SCHEMA (identical on every shard)
-- ============================================================

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    city        VARCHAR(100),
    state       VARCHAR(2),
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category     VARCHAR(100) NOT NULL,
    unit_price   NUMERIC(10,2) NOT NULL,
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id  INTEGER NOT NULL REFERENCES products(product_id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    total_price NUMERIC(10,2) NOT NULL,
    order_date  DATE NOT NULL
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_customers_email    ON customers(email);
CREATE INDEX idx_customers_state    ON customers(state);
CREATE INDEX idx_products_category  ON products(category);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_product_id  ON orders(product_id);
CREATE INDEX idx_orders_order_date  ON orders(order_date);

-- ============================================================
-- SAMPLE DATA
-- ============================================================

-- Southeast customers (FL, GA, TN) - preserving original IDs
INSERT INTO customers (customer_id, first_name, last_name, email, city, state) VALUES
    (1, 'Alice',   'Johnson',  'alice.johnson@example.com',  'Tampa',         'FL'),
    (2, 'Bob',     'Smith',    'bob.smith@example.com',      'Orlando',       'FL'),
    (3, 'Carol',   'Williams', 'carol.williams@example.com', 'Atlanta',       'GA'),
    (4, 'David',   'Brown',    'david.brown@example.com',    'Miami',         'FL'),
    (6, 'Frank',   'Miller',   'frank.miller@example.com',   'Jacksonville',  'FL'),
    (7, 'Grace',   'Wilson',   'grace.wilson@example.com',   'Nashville',     'TN'),
    (8, 'Henry',   'Taylor',   'henry.taylor@example.com',   'Savannah',      'GA');

-- Reset sequence to avoid conflicts with explicit IDs
SELECT setval('customers_customer_id_seq', (SELECT MAX(customer_id) FROM customers));

-- All products (reference table — identical on every shard)
INSERT INTO products (product_id, product_name, category, unit_price) VALUES
    (1,  'Laptop Pro 15',       'Electronics', 1299.99),
    (2,  'Wireless Mouse',      'Electronics',   29.99),
    (3,  'USB-C Hub',           'Electronics',   49.99),
    (4,  'Standing Desk',       'Furniture',    599.99),
    (5,  'Ergonomic Chair',     'Furniture',    449.99),
    (6,  'LED Desk Lamp',       'Furniture',     79.99),
    (7,  'Python Cookbook',      'Books',         45.99),
    (8,  'Data Engineering 101','Books',         39.99),
    (9,  'Noise-Cancel Headset','Electronics',  199.99),
    (10, 'Monitor 27-inch',     'Electronics',  349.99);

SELECT setval('products_product_id_seq', (SELECT MAX(product_id) FROM products));

-- Orders for SE customers only (preserving original order_ids)
INSERT INTO orders (order_id, customer_id, product_id, quantity, total_price, order_date) VALUES
    (1,  1, 1,  1, 1299.99, '2026-01-05'),
    (2,  1, 2,  2,   59.98, '2026-01-05'),
    (3,  2, 4,  1,  599.99, '2026-01-08'),
    (4,  3, 7,  3,  137.97, '2026-01-10'),
    (5,  2, 3,  1,   49.99, '2026-01-12'),
    (6,  4, 5,  1,  449.99, '2026-01-14'),
    (8,  1, 10, 1,  349.99, '2026-01-18'),
    (9,  6, 9,  1,  199.99, '2026-01-20'),
    (10, 3, 1,  1, 1299.99, '2026-01-22'),
    (11, 7, 6,  2,  159.98, '2026-01-23'),
    (12, 4, 2,  3,   89.97, '2026-01-25'),
    (13, 8, 7,  1,   45.99, '2026-01-26'),
    (15, 2, 10, 1,  349.99, '2026-01-30'),
    (16, 6, 1,  1, 1299.99, '2026-02-01'),
    (17, 1, 5,  1,  449.99, '2026-02-03'),
    (18, 3, 3,  2,   99.98, '2026-02-05'),
    (19, 7, 8,  1,   39.99, '2026-02-06'),
    (20, 4, 9,  1,  199.99, '2026-02-08'),
    (21, 8, 6,  1,   79.99, '2026-02-10'),
    (22, 2, 7,  2,   91.98, '2026-02-12'),
    (24, 6, 5,  1,  449.99, '2026-02-16'),
    (25, 1, 3,  1,   49.99, '2026-02-18'),
    (26, 3, 9,  1,  199.99, '2026-02-20'),
    (27, 7, 10, 1,  349.99, '2026-02-22');

SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) FROM orders));
