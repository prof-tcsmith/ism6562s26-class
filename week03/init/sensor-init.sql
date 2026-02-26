-- Week 03: IoT Sensor Database
-- ISM 6562 - Big Data for Business Applications
--
-- Schema: locations → sensors → sensor_readings
-- 10 locations, 50 sensors, 100,000 readings (no indexes on sensor_readings beyond PK)

-- ============================================================
-- Locations Table (10 rows)
-- ============================================================
CREATE TABLE locations (
    location_id   SERIAL PRIMARY KEY,
    building      VARCHAR(50)  NOT NULL,
    floor         INTEGER      NOT NULL,
    room          VARCHAR(20)  NOT NULL,
    description   VARCHAR(200)
);

INSERT INTO locations (building, floor, room, description) VALUES
('Engineering Hall', 1, '101', 'Server room - main data center'),
('Engineering Hall', 1, '102', 'Network operations center'),
('Engineering Hall', 2, '201', 'Research lab - IoT testing'),
('Engineering Hall', 2, '202', 'Graduate student workspace'),
('Science Building', 1, '110', 'Chemistry lab - climate controlled'),
('Science Building', 1, '115', 'Biology cold storage'),
('Science Building', 2, '210', 'Physics instrumentation lab'),
('Library',          1, '100', 'Main reading room'),
('Library',          2, '200', 'Special collections archive'),
('Admin Building',   1, '105', 'IT help desk area');

-- ============================================================
-- Sensors Table (50 rows)
-- 20 temperature, 20 humidity, 10 pressure sensors
-- ============================================================
CREATE TABLE sensors (
    sensor_id     SERIAL PRIMARY KEY,
    sensor_type   VARCHAR(20)  NOT NULL CHECK (sensor_type IN ('temperature', 'humidity', 'pressure')),
    model         VARCHAR(50)  NOT NULL,
    location_id   INTEGER      NOT NULL REFERENCES locations(location_id),
    installed_date DATE        NOT NULL,
    is_active     BOOLEAN      DEFAULT TRUE
);

-- Temperature sensors (20): 2 per location
INSERT INTO sensors (sensor_type, model, location_id, installed_date) VALUES
('temperature', 'TempPro-3000',  1, '2025-06-01'),
('temperature', 'TempPro-3000',  1, '2025-06-01'),
('temperature', 'TempPro-3000',  2, '2025-06-15'),
('temperature', 'TempPro-3000',  2, '2025-06-15'),
('temperature', 'TempPro-5000',  3, '2025-07-01'),
('temperature', 'TempPro-5000',  3, '2025-07-01'),
('temperature', 'TempPro-5000',  4, '2025-07-01'),
('temperature', 'TempPro-5000',  4, '2025-07-01'),
('temperature', 'TempPro-3000',  5, '2025-08-01'),
('temperature', 'TempPro-3000',  5, '2025-08-01'),
('temperature', 'TempPro-3000',  6, '2025-08-15'),
('temperature', 'TempPro-3000',  6, '2025-08-15'),
('temperature', 'TempPro-5000',  7, '2025-09-01'),
('temperature', 'TempPro-5000',  7, '2025-09-01'),
('temperature', 'TempPro-3000',  8, '2025-09-15'),
('temperature', 'TempPro-3000',  8, '2025-09-15'),
('temperature', 'TempPro-5000',  9, '2025-10-01'),
('temperature', 'TempPro-5000',  9, '2025-10-01'),
('temperature', 'TempPro-3000', 10, '2025-10-15'),
('temperature', 'TempPro-3000', 10, '2025-10-15');

-- Humidity sensors (20): 2 per location
INSERT INTO sensors (sensor_type, model, location_id, installed_date) VALUES
('humidity', 'HumidiSense-200',  1, '2025-06-01'),
('humidity', 'HumidiSense-200',  1, '2025-06-01'),
('humidity', 'HumidiSense-200',  2, '2025-06-15'),
('humidity', 'HumidiSense-200',  2, '2025-06-15'),
('humidity', 'HumidiSense-400',  3, '2025-07-01'),
('humidity', 'HumidiSense-400',  3, '2025-07-01'),
('humidity', 'HumidiSense-400',  4, '2025-07-01'),
('humidity', 'HumidiSense-400',  4, '2025-07-01'),
('humidity', 'HumidiSense-200',  5, '2025-08-01'),
('humidity', 'HumidiSense-200',  5, '2025-08-01'),
('humidity', 'HumidiSense-200',  6, '2025-08-15'),
('humidity', 'HumidiSense-200',  6, '2025-08-15'),
('humidity', 'HumidiSense-400',  7, '2025-09-01'),
('humidity', 'HumidiSense-400',  7, '2025-09-01'),
('humidity', 'HumidiSense-200',  8, '2025-09-15'),
('humidity', 'HumidiSense-200',  8, '2025-09-15'),
('humidity', 'HumidiSense-400',  9, '2025-10-01'),
('humidity', 'HumidiSense-400',  9, '2025-10-01'),
('humidity', 'HumidiSense-200', 10, '2025-10-15'),
('humidity', 'HumidiSense-200', 10, '2025-10-15');

-- Pressure sensors (10): 1 per location
INSERT INTO sensors (sensor_type, model, location_id, installed_date) VALUES
('pressure', 'BaroMax-100',  1, '2025-06-01'),
('pressure', 'BaroMax-100',  2, '2025-06-15'),
('pressure', 'BaroMax-100',  3, '2025-07-01'),
('pressure', 'BaroMax-100',  4, '2025-07-01'),
('pressure', 'BaroMax-100',  5, '2025-08-01'),
('pressure', 'BaroMax-100',  6, '2025-08-15'),
('pressure', 'BaroMax-100',  7, '2025-09-01'),
('pressure', 'BaroMax-100',  8, '2025-09-15'),
('pressure', 'BaroMax-100',  9, '2025-10-01'),
('pressure', 'BaroMax-100', 10, '2025-10-15');

-- ============================================================
-- Sensor Readings Table (100,000 rows)
-- Hourly readings over ~83 days (2,000 readings per sensor)
-- Uses generate_series + sin() for realistic patterns
-- NO indexes beyond PK (students will create them)
-- ============================================================
CREATE TABLE sensor_readings (
    reading_id    SERIAL PRIMARY KEY,
    sensor_id     INTEGER        NOT NULL REFERENCES sensors(sensor_id),
    reading_time  TIMESTAMP      NOT NULL,
    value         NUMERIC(10, 2) NOT NULL,
    unit          VARCHAR(10)    NOT NULL
);

-- Generate 100,000 readings: 2,000 per sensor × 50 sensors
-- Each sensor gets hourly readings starting from 2025-11-01
-- Temperature: base ~72°F with daily sin wave ±5°F and per-sensor offset
-- Humidity: base ~45% with daily sin wave ±10% and per-sensor offset
-- Pressure: base ~1013 hPa with slow sin wave ±5 hPa and per-sensor offset
INSERT INTO sensor_readings (sensor_id, reading_time, value, unit)
SELECT
    s.sensor_id,
    ts,
    CASE s.sensor_type
        WHEN 'temperature' THEN
            ROUND((72.0
                + 5.0 * sin(2 * pi() * EXTRACT(EPOCH FROM ts) / 86400)   -- daily cycle
                + (s.sensor_id % 5) * 1.5                                 -- per-sensor offset
                + (random() - 0.5) * 2.0                                  -- noise
            )::numeric, 2)
        WHEN 'humidity' THEN
            ROUND((45.0
                + 10.0 * sin(2 * pi() * EXTRACT(EPOCH FROM ts) / 86400 + pi()/4)  -- daily cycle, phase shifted
                + (s.sensor_id % 5) * 2.0                                          -- per-sensor offset
                + (random() - 0.5) * 3.0                                           -- noise
            )::numeric, 2)
        WHEN 'pressure' THEN
            ROUND((1013.25
                + 5.0 * sin(2 * pi() * EXTRACT(EPOCH FROM ts) / (86400 * 7))  -- weekly cycle
                + (s.sensor_id % 5) * 0.5                                      -- per-sensor offset
                + (random() - 0.5) * 1.0                                       -- noise
            )::numeric, 2)
    END AS value,
    CASE s.sensor_type
        WHEN 'temperature' THEN '°F'
        WHEN 'humidity'    THEN '%'
        WHEN 'pressure'    THEN 'hPa'
    END AS unit
FROM sensors s
CROSS JOIN LATERAL generate_series(
    '2025-11-01 00:00:00'::timestamp,
    '2025-11-01 00:00:00'::timestamp + interval '1999 hours',
    interval '1 hour'
) AS ts;

-- Verify counts
DO $$
DECLARE
    loc_count  INTEGER;
    sen_count  INTEGER;
    read_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO loc_count  FROM locations;
    SELECT COUNT(*) INTO sen_count  FROM sensors;
    SELECT COUNT(*) INTO read_count FROM sensor_readings;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Data loaded successfully:';
    RAISE NOTICE '  Locations:        %', loc_count;
    RAISE NOTICE '  Sensors:          %', sen_count;
    RAISE NOTICE '  Sensor Readings:  %', read_count;
    RAISE NOTICE '========================================';
END $$;
