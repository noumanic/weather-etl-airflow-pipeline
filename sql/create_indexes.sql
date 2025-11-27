-- Weather ETL Pipeline - Index Creation Script
-- Creates indexes to optimize query performance

-- Indexes for weather_records table
CREATE INDEX IF NOT EXISTS idx_city_timestamp 
    ON weather_records(city, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_extraction_date 
    ON weather_records(extraction_date DESC);

CREATE INDEX IF NOT EXISTS idx_city 
    ON weather_records(city);

CREATE INDEX IF NOT EXISTS idx_timestamp 
    ON weather_records(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_temperature_celsius 
    ON weather_records(temperature_celsius);

CREATE INDEX IF NOT EXISTS idx_weather_condition 
    ON weather_records(weather_condition);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_city_extraction_date 
    ON weather_records(city, extraction_date DESC);

-- Indexes for daily_weather_stats table
CREATE INDEX IF NOT EXISTS idx_stats_city_date 
    ON daily_weather_stats(city, date DESC);

CREATE INDEX IF NOT EXISTS idx_stats_date 
    ON daily_weather_stats(date DESC);

CREATE INDEX IF NOT EXISTS idx_stats_city 
    ON daily_weather_stats(city);

-- Indexes for etl_audit_log table
CREATE INDEX IF NOT EXISTS idx_audit_run_date 
    ON etl_audit_log(run_date DESC);

CREATE INDEX IF NOT EXISTS idx_audit_status 
    ON etl_audit_log(status);

CREATE INDEX IF NOT EXISTS idx_audit_pipeline 
    ON etl_audit_log(pipeline_name, run_date DESC);

-- Analyze tables to update statistics
ANALYZE weather_records;
ANALYZE daily_weather_stats;
ANALYZE etl_audit_log;
