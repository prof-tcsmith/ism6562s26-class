-- Sales Operational Database
-- ISM 6562 - Week 03 Assignment
--
-- Normalized schema for a sales transaction system.
-- Tables: customers, products, orders

-- ============================================================
-- SCHEMA
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

INSERT INTO customers (first_name, last_name, email, city, state) VALUES
    ('Alice',   'Johnson',  'alice.johnson@example.com',  'Tampa',         'FL'),
    ('Bob',     'Smith',    'bob.smith@example.com',      'Orlando',       'FL'),
    ('Carol',   'Williams', 'carol.williams@example.com', 'Atlanta',       'GA'),
    ('David',   'Brown',    'david.brown@example.com',    'Miami',         'FL'),
    ('Eva',     'Davis',    'eva.davis@example.com',      'Charlotte',     'NC'),
    ('Frank',   'Miller',   'frank.miller@example.com',   'Jacksonville',  'FL'),
    ('Grace',   'Wilson',   'grace.wilson@example.com',   'Nashville',     'TN'),
    ('Henry',   'Taylor',   'henry.taylor@example.com',   'Savannah',      'GA');

INSERT INTO products (product_name, category, unit_price) VALUES
    ('Laptop Pro 15',       'Electronics', 1299.99),
    ('Wireless Mouse',      'Electronics',   29.99),
    ('USB-C Hub',           'Electronics',   49.99),
    ('Standing Desk',       'Furniture',    599.99),
    ('Ergonomic Chair',     'Furniture',    449.99),
    ('LED Desk Lamp',       'Furniture',     79.99),
    ('Python Cookbook',      'Books',         45.99),
    ('Data Engineering 101','Books',         39.99),
    ('Noise-Cancel Headset','Electronics',  199.99),
    ('Monitor 27-inch',     'Electronics',  349.99);

INSERT INTO orders (customer_id, product_id, quantity, total_price, order_date) VALUES
    (1, 1, 1, 1299.99, '2026-01-05'),
    (1, 2, 2,   59.98, '2026-01-05'),
    (2, 4, 1,  599.99, '2026-01-08'),
    (3, 7, 3,  137.97, '2026-01-10'),
    (2, 3, 1,   49.99, '2026-01-12'),
    (4, 5, 1,  449.99, '2026-01-14'),
    (5, 8, 2,   79.98, '2026-01-15'),
    (1, 10,1,  349.99, '2026-01-18'),
    (6, 9, 1,  199.99, '2026-01-20'),
    (3, 1, 1, 1299.99, '2026-01-22'),
    (7, 6, 2,  159.98, '2026-01-23'),
    (4, 2, 3,   89.97, '2026-01-25'),
    (8, 7, 1,   45.99, '2026-01-26'),
    (5, 4, 1,  599.99, '2026-01-28'),
    (2, 10,1,  349.99, '2026-01-30'),
    (6, 1, 1, 1299.99, '2026-02-01'),
    (1, 5, 1,  449.99, '2026-02-03'),
    (3, 3, 2,   99.98, '2026-02-05'),
    (7, 8, 1,   39.99, '2026-02-06'),
    (4, 9, 1,  199.99, '2026-02-08'),
    (8, 6, 1,   79.99, '2026-02-10'),
    (2, 7, 2,   91.98, '2026-02-12'),
    (5, 1, 1, 1299.99, '2026-02-14'),
    (6, 5, 1,  449.99, '2026-02-16'),
    (1, 3, 1,   49.99, '2026-02-18'),
    (3, 9, 1,  199.99, '2026-02-20'),
    (7, 10,1,  349.99, '2026-02-22');
