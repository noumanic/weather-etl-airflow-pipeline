"""Simple local runner for ETL steps (without Airflow).
This script is intended for quick manual testing of the extract/transform logic.
"""
from datetime import datetime, timezone
import sys
import os

# Add project root to path so we can import from dags
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dags.helpers import call_open_meteo_api, to_fahrenheit

## Local copy of cities to avoid importing Airflow code when testing locally
CITIES = [
    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
]


def run_local_etl():
    print(f"ETL Local Run: {datetime.now(timezone.utc)}")
    results = []
    for city in CITIES:
        try:
            # Use shared helper
            w = call_open_meteo_api(city)
            
            # Transform
            w['temperature_fahrenheit'] = to_fahrenheit(w['temperature_celsius'])
            w['extraction_date'] = datetime.now(timezone.utc)
            
            results.append(w)
            print(f"{w['city']}: {w['temperature_celsius']}°C -> {w['temperature_fahrenheit']}°F; Humidity={w['humidity']}")
        except Exception as e:
            print(f"Error processing city {city['name']}: {e}")
    print("\nFinished Local ETL run.")


if __name__ == '__main__':
    run_local_etl()
