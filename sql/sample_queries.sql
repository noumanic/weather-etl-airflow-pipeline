-- Weather ETL Pipeline - Sample Queries
-- Useful queries for analyzing weather data

-- ========================================
-- Basic Queries
-- ========================================

-- Get latest weather data for all cities
SELECT 
    city,
    temperature_celsius,
    temperature_fahrenheit,
    humidity,
    wind_speed,
    weather_condition,
    timestamp
FROM weather_records
WHERE extraction_date >= CURRENT_DATE
ORDER BY city, timestamp DESC;

-- Get weather data for a specific city
SELECT *
FROM weather_records
WHERE city = 'New York'
ORDER BY timestamp DESC
LIMIT 10;

-- ========================================
-- Temperature Analysis
-- ========================================

-- Average temperature by city (last 7 days)
SELECT 
    city,
    ROUND(AVG(temperature_celsius), 2) as avg_temp_celsius,
    ROUND(AVG(temperature_fahrenheit), 2) as avg_temp_fahrenheit,
    ROUND(MIN(temperature_celsius), 2) as min_temp_celsius,
    ROUND(MAX(temperature_celsius), 2) as max_temp_celsius
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY city
ORDER BY avg_temp_celsius DESC;

-- Hottest and coldest cities today
SELECT 
    'Hottest' as category,
    city,
    MAX(temperature_celsius) as temperature_celsius,
    MAX(temperature_fahrenheit) as temperature_fahrenheit
FROM weather_records
WHERE DATE(extraction_date) = CURRENT_DATE
GROUP BY city
ORDER BY temperature_celsius DESC
LIMIT 5

UNION ALL

SELECT 
    'Coldest' as category,
    city,
    MIN(temperature_celsius) as temperature_celsius,
    MIN(temperature_fahrenheit) as temperature_fahrenheit
FROM weather_records
WHERE DATE(extraction_date) = CURRENT_DATE
GROUP BY city
ORDER BY temperature_celsius ASC
LIMIT 5;

-- ========================================
-- Time Series Analysis
-- ========================================

-- Temperature trend for a city over last 30 days
SELECT 
    DATE(timestamp) as date,
    city,
    ROUND(AVG(temperature_celsius), 2) as avg_temp,
    ROUND(MIN(temperature_celsius), 2) as min_temp,
    ROUND(MAX(temperature_celsius), 2) as max_temp
FROM weather_records
WHERE city = 'New York'
    AND timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(timestamp), city
ORDER BY date DESC;

-- Hourly temperature pattern
SELECT 
    EXTRACT(HOUR FROM timestamp) as hour,
    city,
    ROUND(AVG(temperature_celsius), 2) as avg_temp
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY EXTRACT(HOUR FROM timestamp), city
ORDER BY city, hour;

-- ========================================
-- Weather Conditions
-- ========================================

-- Most common weather conditions by city
SELECT 
    city,
    weather_condition,
    COUNT(*) as occurrences,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 2) as percentage
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY city, weather_condition
ORDER BY city, occurrences DESC;

-- Rainy days count by city
SELECT 
    city,
    COUNT(DISTINCT DATE(timestamp)) as rainy_days
FROM weather_records
WHERE weather_condition LIKE '%rain%'
    AND extraction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY city
ORDER BY rainy_days DESC;

-- ========================================
-- Humidity and Wind Analysis
-- ========================================

-- Average humidity and wind speed by city
SELECT 
    city,
    ROUND(AVG(humidity), 2) as avg_humidity,
    ROUND(AVG(wind_speed), 2) as avg_wind_speed,
    ROUND(MAX(wind_speed), 2) as max_wind_speed
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY city
ORDER BY avg_humidity DESC;

-- Cities with high humidity (> 80%)
SELECT 
    city,
    DATE(timestamp) as date,
    AVG(humidity) as avg_humidity
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY city, DATE(timestamp)
HAVING AVG(humidity) > 80
ORDER BY avg_humidity DESC;

-- ========================================
-- Daily Statistics Queries
-- ========================================

-- Latest daily statistics
SELECT *
FROM daily_weather_stats
ORDER BY date DESC, city
LIMIT 20;

-- Temperature range by city (max - min)
SELECT 
    city,
    date,
    max_temp_celsius - min_temp_celsius as temp_range_celsius,
    max_temp_fahrenheit - min_temp_fahrenheit as temp_range_fahrenheit
FROM daily_weather_stats
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY temp_range_celsius DESC;

-- ========================================
-- Data Quality Queries
-- ========================================

-- Check for missing data
SELECT 
    DATE(extraction_date) as date,
    COUNT(*) as total_records,
    SUM(CASE WHEN temperature_celsius IS NULL THEN 1 ELSE 0 END) as null_temperature,
    SUM(CASE WHEN humidity IS NULL THEN 1 ELSE 0 END) as null_humidity,
    SUM(CASE WHEN wind_speed IS NULL THEN 1 ELSE 0 END) as null_wind_speed
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(extraction_date)
ORDER BY date DESC;

-- Check for data freshness
SELECT 
    city,
    MAX(extraction_date) as last_update,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(extraction_date)))/3600 as hours_since_update
FROM weather_records
GROUP BY city
ORDER BY last_update DESC;

-- Records per day
SELECT 
    DATE(extraction_date) as date,
    COUNT(*) as record_count,
    COUNT(DISTINCT city) as cities_count
FROM weather_records
GROUP BY DATE(extraction_date)
ORDER BY date DESC
LIMIT 30;

-- ========================================
-- Comparison Queries
-- ========================================

-- Compare today vs yesterday average temperatures
WITH today AS (
    SELECT 
        city,
        AVG(temperature_celsius) as avg_temp
    FROM weather_records
    WHERE DATE(extraction_date) = CURRENT_DATE
    GROUP BY city
),
yesterday AS (
    SELECT 
        city,
        AVG(temperature_celsius) as avg_temp
    FROM weather_records
    WHERE DATE(extraction_date) = CURRENT_DATE - INTERVAL '1 day'
    GROUP BY city
)
SELECT 
    t.city,
    ROUND(t.avg_temp, 2) as today_avg,
    ROUND(y.avg_temp, 2) as yesterday_avg,
    ROUND(t.avg_temp - y.avg_temp, 2) as temp_change
FROM today t
LEFT JOIN yesterday y ON t.city = y.city
ORDER BY ABS(t.avg_temp - y.avg_temp) DESC;

-- ========================================
-- ETL Audit Queries
-- ========================================

-- Recent pipeline runs
SELECT 
    pipeline_name,
    run_date,
    status,
    records_processed,
    execution_time_seconds
FROM etl_audit_log
ORDER BY run_date DESC
LIMIT 20;

-- Pipeline success rate
SELECT 
    pipeline_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs,
    ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM etl_audit_log
GROUP BY pipeline_name;
