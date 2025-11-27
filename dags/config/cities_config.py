"""
Cities configuration for weather data collection
"""

CITIES = [
    {
        "name": "New York",
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "country": "USA"
    },
    {
        "name": "London",
        "lat": 51.5074,
        "lon": -0.1278,
        "timezone": "Europe/London",
        "country": "UK"
    },
    {
        "name": "Tokyo",
        "lat": 35.6762,
        "lon": 139.6503,
        "timezone": "Asia/Tokyo",
        "country": "Japan"
    },
    {
        "name": "Sydney",
        "lat": -33.8688,
        "lon": 151.2093,
        "timezone": "Australia/Sydney",
        "country": "Australia"
    },
    {
        "name": "Dubai",
        "lat": 25.2048,
        "lon": 55.2708,
        "timezone": "Asia/Dubai",
        "country": "UAE"
    }
]

# API Configuration
API_CONFIG = {
    "base_url": "https://api.open-meteo.com/v1/forecast",
    "timeout": 10,
    "max_retries": 3,
    "retry_delay": 300  # seconds
}

# Database Configuration
DB_CONFIG = {
    "table_name": "weather_data",
    "schema": "public"
}