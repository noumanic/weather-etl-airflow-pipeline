-- Weather ETL Pipeline - Table Creation Script
-- Creates all necessary tables for the weather data warehouse

-- Create weather_records table
CREATE TABLE IF NOT EXISTS weather_records (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    temperature_celsius DECIMAL(5, 2),
    temperature_fahrenheit DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    weather_condition VARCHAR(100),
    timestamp TIMESTAMP NOT NULL,
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT check_temperature_range CHECK (
        temperature_celsius >= -100 AND temperature_celsius <= 100
    ),
    CONSTRAINT check_humidity_range CHECK (
        humidity >= 0 AND humidity <= 100
    ),
    CONSTRAINT check_wind_speed CHECK (
        wind_speed >= 0
    )
);

-- Create daily_weather_stats table
CREATE TABLE IF NOT EXISTS daily_weather_stats (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    avg_temp_celsius DECIMAL(5, 2),
    avg_temp_fahrenheit DECIMAL(5, 2),
    max_temp_celsius DECIMAL(5, 2),
    max_temp_fahrenheit DECIMAL(5, 2),
    min_temp_celsius DECIMAL(5, 2),
    min_temp_fahrenheit DECIMAL(5, 2),
    avg_humidity DECIMAL(5, 2),
    avg_wind_speed DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicate statistics
    UNIQUE(city, date)
);

-- Create audit log table
CREATE TABLE IF NOT EXISTS etl_audit_log (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    records_processed INTEGER,
    error_message TEXT,
    execution_time_seconds DECIMAL(10, 2)
);

-- Add comments to tables
COMMENT ON TABLE weather_records IS 'Stores raw weather data records from API';
COMMENT ON TABLE daily_weather_stats IS 'Stores aggregated daily weather statistics';
COMMENT ON TABLE etl_audit_log IS 'Tracks ETL pipeline execution history';

-- Add comments to important columns
COMMENT ON COLUMN weather_records.temperature_celsius IS 'Temperature in Celsius from API';
COMMENT ON COLUMN weather_records.temperature_fahrenheit IS 'Converted temperature in Fahrenheit';
COMMENT ON COLUMN weather_records.extraction_date IS 'Timestamp when data was extracted from API';
COMMENT ON COLUMN weather_records.timestamp IS 'Actual weather measurement timestamp from API';
