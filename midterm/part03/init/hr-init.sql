-- HR Operational Database
-- ISM 6562 - Week 03 Assignment
--
-- Normalized schema for a human resources system.
-- Tables: departments, employees, timesheets

-- ============================================================
-- SCHEMA
-- ============================================================

CREATE TABLE departments (
    department_id   SERIAL PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL,
    location        VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    employee_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    hire_date     DATE NOT NULL,
    job_title     VARCHAR(100) NOT NULL
);

CREATE TABLE timesheets (
    timesheet_id  SERIAL PRIMARY KEY,
    employee_id   INTEGER NOT NULL REFERENCES employees(employee_id),
    work_date     DATE NOT NULL,
    hours_worked  NUMERIC(4,2) NOT NULL CHECK (hours_worked >= 0 AND hours_worked <= 24),
    UNIQUE(employee_id, work_date)
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_employees_department_id ON employees(department_id);
CREATE INDEX idx_employees_hire_date     ON employees(hire_date);
CREATE INDEX idx_timesheets_employee_id  ON timesheets(employee_id);
CREATE INDEX idx_timesheets_work_date    ON timesheets(work_date);

-- ============================================================
-- SAMPLE DATA
-- ============================================================

INSERT INTO departments (department_name, location) VALUES
    ('Engineering',  'Tampa'),
    ('Marketing',    'Orlando'),
    ('Sales',        'Miami'),
    ('Human Resources', 'Tampa');

INSERT INTO employees (first_name, last_name, email, department_id, hire_date, job_title) VALUES
    ('Maria',   'Garcia',    'maria.garcia@company.com',    1, '2023-03-15', 'Senior Engineer'),
    ('James',   'Lee',       'james.lee@company.com',       1, '2024-01-10', 'Software Engineer'),
    ('Sarah',   'Chen',      'sarah.chen@company.com',      1, '2024-06-01', 'Data Engineer'),
    ('Michael', 'Patel',     'michael.patel@company.com',   2, '2023-07-20', 'Marketing Manager'),
    ('Lisa',    'Thompson',  'lisa.thompson@company.com',   2, '2024-09-01', 'Content Specialist'),
    ('Robert',  'Kim',       'robert.kim@company.com',      2, '2025-01-15', 'Marketing Analyst'),
    ('Jennifer','Martinez',  'jennifer.martinez@company.com',3, '2023-05-10', 'Sales Director'),
    ('William', 'Anderson',  'william.anderson@company.com',3, '2024-02-28', 'Account Executive'),
    ('Amanda',  'Jackson',   'amanda.jackson@company.com',  3, '2024-11-01', 'Sales Representative'),
    ('Daniel',  'White',     'daniel.white@company.com',    4, '2023-01-05', 'HR Director'),
    ('Emily',   'Harris',    'emily.harris@company.com',    4, '2024-04-15', 'HR Specialist'),
    ('Kevin',   'Robinson',  'kevin.robinson@company.com',  4, '2025-02-01', 'Recruiter');

-- Generate timesheet entries for January and February 2026
-- Each employee works most weekdays with varying hours

INSERT INTO timesheets (employee_id, work_date, hours_worked) VALUES
    -- Week of Jan 5-9
    (1,  '2026-01-05', 8.0), (2,  '2026-01-05', 7.5), (3,  '2026-01-05', 8.0),
    (4,  '2026-01-05', 8.0), (5,  '2026-01-05', 7.0), (6,  '2026-01-05', 8.0),
    (7,  '2026-01-05', 8.5), (8,  '2026-01-05', 8.0), (9,  '2026-01-05', 7.5),
    (10, '2026-01-05', 8.0), (11, '2026-01-05', 7.5), (12, '2026-01-05', 6.0),
    (1,  '2026-01-06', 8.5), (2,  '2026-01-06', 8.0), (3,  '2026-01-06', 7.5),
    (4,  '2026-01-06', 7.0), (5,  '2026-01-06', 8.0), (7,  '2026-01-06', 8.0),
    (8,  '2026-01-06', 7.5), (10, '2026-01-06', 8.0), (11, '2026-01-06', 8.5),
    -- Week of Jan 12-16
    (1,  '2026-01-12', 8.0), (2,  '2026-01-12', 8.0), (3,  '2026-01-12', 8.5),
    (4,  '2026-01-12', 8.0), (5,  '2026-01-12', 7.5), (6,  '2026-01-12', 8.0),
    (7,  '2026-01-12', 7.0), (8,  '2026-01-12', 8.0), (9,  '2026-01-12', 8.0),
    (10, '2026-01-12', 7.5), (11, '2026-01-12', 8.0), (12, '2026-01-12', 7.0),
    (1,  '2026-01-13', 7.5), (2,  '2026-01-13', 8.0), (3,  '2026-01-13', 8.0),
    (4,  '2026-01-13', 8.5), (6,  '2026-01-13', 7.5), (7,  '2026-01-13', 8.0),
    (9,  '2026-01-13', 7.5), (10, '2026-01-13', 8.0), (12, '2026-01-13', 8.0),
    -- Week of Jan 19-23
    (1,  '2026-01-19', 8.0), (2,  '2026-01-19', 7.0), (3,  '2026-01-19', 8.0),
    (5,  '2026-01-19', 8.0), (6,  '2026-01-19', 7.5), (7,  '2026-01-19', 8.5),
    (8,  '2026-01-19', 8.0), (9,  '2026-01-19', 7.0), (11, '2026-01-19', 8.0),
    (1,  '2026-01-20', 8.5), (3,  '2026-01-20', 7.5), (4,  '2026-01-20', 8.0),
    (5,  '2026-01-20', 8.0), (7,  '2026-01-20', 7.0), (8,  '2026-01-20', 8.0),
    (10, '2026-01-20', 8.0), (11, '2026-01-20', 7.5), (12, '2026-01-20', 8.0),
    -- Week of Jan 26-30
    (1,  '2026-01-26', 7.5), (2,  '2026-01-26', 8.0), (3,  '2026-01-26', 8.0),
    (4,  '2026-01-26', 7.5), (5,  '2026-01-26', 8.0), (6,  '2026-01-26', 8.5),
    (7,  '2026-01-26', 8.0), (8,  '2026-01-26', 7.0), (9,  '2026-01-26', 8.0),
    (10, '2026-01-26', 8.0), (11, '2026-01-26', 7.0), (12, '2026-01-26', 8.0),
    -- Week of Feb 2-6
    (1,  '2026-02-02', 8.0), (2,  '2026-02-02', 8.5), (3,  '2026-02-02', 7.0),
    (4,  '2026-02-02', 8.0), (5,  '2026-02-02', 7.5), (6,  '2026-02-02', 8.0),
    (7,  '2026-02-02', 8.0), (8,  '2026-02-02', 8.5), (9,  '2026-02-02', 8.0),
    (10, '2026-02-02', 7.5), (11, '2026-02-02', 8.0), (12, '2026-02-02', 7.0),
    (1,  '2026-02-03', 8.0), (2,  '2026-02-03', 7.5), (4,  '2026-02-03', 8.0),
    (5,  '2026-02-03', 8.0), (7,  '2026-02-03', 7.5), (9,  '2026-02-03', 8.0),
    (10, '2026-02-03', 8.5), (11, '2026-02-03', 7.0),
    -- Week of Feb 9-13
    (1,  '2026-02-09', 8.0), (2,  '2026-02-09', 8.0), (3,  '2026-02-09', 8.5),
    (4,  '2026-02-09', 7.5), (5,  '2026-02-09', 8.0), (6,  '2026-02-09', 7.0),
    (7,  '2026-02-09', 8.0), (8,  '2026-02-09', 7.5), (9,  '2026-02-09', 8.0),
    (10, '2026-02-09', 8.0), (11, '2026-02-09', 8.5), (12, '2026-02-09', 8.0);
