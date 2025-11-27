-- Create data quality dashboard view
CREATE OR REPLACE VIEW v_data_quality_dashboard AS
SELECT 
    DATE(extraction_date) as date,
    COUNT(*) as total_records,
    COUNT(DISTINCT city) as cities_count,
    COUNT(*) FILTER (WHERE temperature_celsius IS NULL) as missing_temperature,
    COUNT(*) FILTER (WHERE humidity IS NULL) as missing_humidity,
    COUNT(*) FILTER (WHERE wind_speed IS NULL) as missing_wind_speed,
    COUNT(*) FILTER (WHERE temperature_celsius < -100 OR temperature_celsius > 100) as invalid_temperature,
    COUNT(*) FILTER (WHERE humidity < 0 OR humidity > 100) as invalid_humidity,
    ROUND(
        (COUNT(*) - 
         COUNT(*) FILTER (WHERE temperature_celsius IS NULL OR humidity IS NULL OR wind_speed IS NULL)
        )::NUMERIC / COUNT(*) * 100, 2
    ) as data_completeness_pct
FROM weather_records
GROUP BY DATE(extraction_date)
ORDER BY date DESC;

-- Grant view permissions
GRANT SELECT ON v_data_quality_dashboard TO weather_user;

