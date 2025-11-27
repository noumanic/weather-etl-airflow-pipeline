"""
Cities Configuration for Weather ETL Pipeline
Configure the cities for which weather data will be collected.
"""

# List of cities with their coordinates
CITIES = [
    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093},
    {"name": "Dubai", "latitude": 25.2048, "longitude": 55.2708},
    {"name": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Toronto", "latitude": 43.6532, "longitude": -79.3832},
    {"name": "Berlin", "latitude": 52.5200, "longitude": 13.4050},
]

# You can also organize cities by region
CITIES_BY_REGION = {
    "North America": [
        {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
        {"name": "Toronto", "latitude": 43.6532, "longitude": -79.3832},
        {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437},
    ],
    "Europe": [
        {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
        {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
        {"name": "Berlin", "latitude": 52.5200, "longitude": 13.4050},
    ],
    "Asia": [
        {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
        {"name": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
        {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    ],
    "Middle East": [
        {"name": "Dubai", "latitude": 25.2048, "longitude": 55.2708},
    ],
    "Oceania": [
        {"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093},
    ],
}
