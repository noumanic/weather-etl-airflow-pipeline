-- Create weather database
CREATE DATABASE weather_data;

-- Connect to weather database
\c weather_data;

-- Create weather user
CREATE USER weather_user WITH PASSWORD 'weather_pass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE weather_data TO weather_user;

-- Create weather table
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant table privileges
GRANT ALL PRIVILEGES ON TABLE weather_records TO weather_user;
GRANT USAGE, SELECT ON SEQUENCE weather_records_id_seq TO weather_user;

-- Create index for better query performance
CREATE INDEX idx_city_timestamp ON weather_records(city, timestamp);
CREATE INDEX idx_extraction_date ON weather_records(extraction_date);

-- Create daily statistics table
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
    UNIQUE(city, date)
);

-- Grant table privileges for stats table
GRANT ALL PRIVILEGES ON TABLE daily_weather_stats TO weather_user;
GRANT USAGE, SELECT ON SEQUENCE daily_weather_stats_id_seq TO weather_user;