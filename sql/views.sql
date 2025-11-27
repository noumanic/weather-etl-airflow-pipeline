-- Weather ETL Pipeline - Analytical Views
-- Creates views for common analytical queries

-- ========================================
-- Current Weather View
-- ========================================
CREATE OR REPLACE VIEW v_current_weather AS
SELECT DISTINCT ON (city)
    city,
    temperature_celsius,
    temperature_fahrenheit,
    humidity,
    wind_speed,
    weather_condition,
    timestamp as measurement_time,
    extraction_date
FROM weather_records
ORDER BY city, extraction_date DESC, timestamp DESC;

COMMENT ON VIEW v_current_weather IS 'Latest weather data for each city';

-- ========================================
-- Daily Weather Summary View
-- ========================================
CREATE OR REPLACE VIEW v_daily_weather_summary AS
SELECT 
    DATE(timestamp) as date,
    city,
    COUNT(*) as measurements_count,
    ROUND(AVG(temperature_celsius), 2) as avg_temp_celsius,
    ROUND(AVG(temperature_fahrenheit), 2) as avg_temp_fahrenheit,
    ROUND(MIN(temperature_celsius), 2) as min_temp_celsius,
    ROUND(MAX(temperature_celsius), 2) as max_temp_celsius,
    ROUND(AVG(humidity), 2) as avg_humidity,
    ROUND(AVG(wind_speed), 2) as avg_wind_speed,
    MODE() WITHIN GROUP (ORDER BY weather_condition) as most_common_condition
FROM weather_records
GROUP BY DATE(timestamp), city;

COMMENT ON VIEW v_daily_weather_summary IS 'Daily aggregated weather statistics';

-- ========================================
-- Weekly Weather Trends View
-- ========================================
CREATE OR REPLACE VIEW v_weekly_weather_trends AS
SELECT 
    DATE_TRUNC('week', timestamp) as week_start,
    city,
    COUNT(*) as measurements_count,
    ROUND(AVG(temperature_celsius), 2) as avg_temp_celsius,
    ROUND(MIN(temperature_celsius), 2) as min_temp_celsius,
    ROUND(MAX(temperature_celsius), 2) as max_temp_celsius,
    ROUND(AVG(humidity), 2) as avg_humidity,
    ROUND(AVG(wind_speed), 2) as avg_wind_speed
FROM weather_records
GROUP BY DATE_TRUNC('week', timestamp), city;

COMMENT ON VIEW v_weekly_weather_trends IS 'Weekly aggregated weather trends';

-- ========================================
-- Temperature Extremes View
-- ========================================
CREATE OR REPLACE VIEW v_temperature_extremes AS
WITH ranked_temps AS (
    SELECT 
        city,
        temperature_celsius,
        temperature_fahrenheit,
        timestamp,
        RANK() OVER (PARTITION BY city ORDER BY temperature_celsius DESC) as heat_rank,
        RANK() OVER (PARTITION BY city ORDER BY temperature_celsius ASC) as cold_rank
    FROM weather_records
    WHERE extraction_date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    city,
    MAX(CASE WHEN heat_rank = 1 THEN temperature_celsius END) as highest_temp_celsius,
    MAX(CASE WHEN heat_rank = 1 THEN temperature_fahrenheit END) as highest_temp_fahrenheit,
    MAX(CASE WHEN heat_rank = 1 THEN timestamp END) as highest_temp_time,
    MAX(CASE WHEN cold_rank = 1 THEN temperature_celsius END) as lowest_temp_celsius,
    MAX(CASE WHEN cold_rank = 1 THEN temperature_fahrenheit END) as lowest_temp_fahrenheit,
    MAX(CASE WHEN cold_rank = 1 THEN timestamp END) as lowest_temp_time
FROM ranked_temps
GROUP BY city;

COMMENT ON VIEW v_temperature_extremes IS 'Highest and lowest temperatures per city (last 30 days)';

-- ========================================
-- Weather Conditions Summary View
-- ========================================
CREATE OR REPLACE VIEW v_weather_conditions_summary AS
SELECT 
    city,
    weather_condition,
    COUNT(*) as occurrence_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 2) as percentage,
    MIN(timestamp) as first_occurrence,
    MAX(timestamp) as last_occurrence
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY city, weather_condition;

COMMENT ON VIEW v_weather_conditions_summary IS 'Weather conditions frequency by city (last 30 days)';

-- ========================================
-- Data Quality Dashboard View
-- ========================================
CREATE OR REPLACE VIEW v_data_quality_dashboard AS
SELECT 
    DATE(extraction_date) as date,
    COUNT(*) as total_records,
    COUNT(DISTINCT city) as cities_count,
    SUM(CASE WHEN temperature_celsius IS NULL THEN 1 ELSE 0 END) as missing_temperature,
    SUM(CASE WHEN humidity IS NULL THEN 1 ELSE 0 END) as missing_humidity,
    SUM(CASE WHEN wind_speed IS NULL THEN 1 ELSE 0 END) as missing_wind_speed,
    SUM(CASE WHEN temperature_celsius < -50 OR temperature_celsius > 60 THEN 1 ELSE 0 END) as invalid_temperature,
    SUM(CASE WHEN humidity < 0 OR humidity > 100 THEN 1 ELSE 0 END) as invalid_humidity,
    ROUND(
        (COUNT(*) - SUM(CASE 
            WHEN temperature_celsius IS NULL 
                OR humidity IS NULL 
                OR wind_speed IS NULL 
            THEN 1 ELSE 0 END)
        ) * 100.0 / COUNT(*), 2
    ) as data_completeness_pct
FROM weather_records
GROUP BY DATE(extraction_date)
ORDER BY date DESC;

COMMENT ON VIEW v_data_quality_dashboard IS 'Data quality metrics by date';

-- ========================================
-- City Comparison View
-- ========================================
CREATE OR REPLACE VIEW v_city_comparison AS
SELECT 
    city,
    COUNT(*) as total_measurements,
    ROUND(AVG(temperature_celsius), 2) as avg_temp_celsius,
    ROUND(MIN(temperature_celsius), 2) as min_temp_celsius,
    ROUND(MAX(temperature_celsius), 2) as max_temp_celsius,
    ROUND(STDDEV(temperature_celsius), 2) as temp_std_dev,
    ROUND(AVG(humidity), 2) as avg_humidity,
    ROUND(AVG(wind_speed), 2) as avg_wind_speed,
    MAX(extraction_date) as last_update
FROM weather_records
WHERE extraction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY city;

COMMENT ON VIEW v_city_comparison IS 'Comparative statistics across cities (last 7 days)';

-- ========================================
-- Pipeline Performance View
-- ========================================
CREATE OR REPLACE VIEW v_pipeline_performance AS
SELECT 
    DATE(run_date) as run_date,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs,
    SUM(CASE WHEN status = 'FAILURE' THEN 1 ELSE 0 END) as failed_runs,
    SUM(records_processed) as total_records_processed,
    ROUND(AVG(execution_time_seconds), 2) as avg_execution_time,
    ROUND(MIN(execution_time_seconds), 2) as min_execution_time,
    ROUND(MAX(execution_time_seconds), 2) as max_execution_time
FROM etl_audit_log
GROUP BY DATE(run_date)
ORDER BY run_date DESC;

COMMENT ON VIEW v_pipeline_performance IS 'ETL pipeline performance metrics by date';

-- ========================================
-- Grant Access to Views
-- ========================================
GRANT SELECT ON v_current_weather TO weather_user;
GRANT SELECT ON v_daily_weather_summary TO weather_user;
GRANT SELECT ON v_weekly_weather_trends TO weather_user;
GRANT SELECT ON v_temperature_extremes TO weather_user;
GRANT SELECT ON v_weather_conditions_summary TO weather_user;
GRANT SELECT ON v_data_quality_dashboard TO weather_user;
GRANT SELECT ON v_city_comparison TO weather_user;
GRANT SELECT ON v_pipeline_performance TO weather_user;
