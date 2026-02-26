-- Sales Shard: Northeast (NC and others)
-- ISM 6562 - Midterm Part 2
--
-- This shard contains customers located in North Carolina (and any future
-- states outside the Southeast region).
-- 1 customer, ~3 orders, all 10 products (reference table).

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

-- Northeast customers (NC) - preserving original IDs
INSERT INTO customers (customer_id, first_name, last_name, email, city, state) VALUES
    (5, 'Eva', 'Davis', 'eva.davis@example.com', 'Charlotte', 'NC');

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

-- Orders for NE customers only (preserving original order_ids)
INSERT INTO orders (order_id, customer_id, product_id, quantity, total_price, order_date) VALUES
    (7,  5, 8, 2,   79.98, '2026-01-15'),
    (14, 5, 4, 1,  599.99, '2026-01-28'),
    (23, 5, 1, 1, 1299.99, '2026-02-14');

SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) FROM orders));
