# Open-Meteo API Integration Documentation

This document explains how the Weather ETL Pipeline integrates with the Open-Meteo API.

## Overview

The pipeline uses the Open-Meteo Weather API to fetch real-time weather data for multiple cities worldwide.

**API Endpoint**: `https://api.open-meteo.com/v1/forecast`

**Features**:
- Free, no API key required
- Global coverage
- Hourly and daily forecasts
- Current weather conditions
- Historical data (when needed)

## API Integration

### Request Format

```python
import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    'latitude': 40.7128,
    'longitude': -74.0060,
    'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
    'timezone': 'auto'
}

response = requests.get(url, params=params, timeout=10)
data = response.json()
```

### Parameters Used

| Parameter | Value | Description |
|-----------|-------|-------------|
| `latitude` | Float | Latitude coordinate (-90 to 90) |
| `longitude` | Float | Longitude coordinate (-180 to 180) |
| `current` | String | Comma-separated list of variables |
| `timezone` | String | Time zone (auto-detect or IANA format) |

### Current Weather Variables

| Variable | Description | Unit |
|----------|-------------|------|
| `temperature_2m` | Temperature at 2 meters height | °C |
| `relative_humidity_2m` | Relative humidity | % |
| `wind_speed_10m` | Wind speed at 10 meters | m/s |
| `weather_code` | WMO weather condition code | Integer |

### Response Format

```json
{
  "latitude": 40.71,
  "longitude": -74.01,
  "generationtime_ms": 0.123,
  "utc_offset_seconds": -18000,
  "timezone": "America/New_York",
  "timezone_abbreviation": "EST",
  "elevation": 7.0,
  "current_units": {
    "time": "iso8601",
    "interval": "seconds",
    "temperature_2m": "°C",
    "relative_humidity_2m": "%",
    "wind_speed_10m": "m/s",
    "weather_code": "wmo code"
  },
  "current": {
    "time": "2024-01-15T12:00",
    "interval": 900,
    "temperature_2m": 5.2,
    "relative_humidity_2m": 65,
    "wind_speed_10m": 8.5,
    "weather_code": 3
  }
}
```

## Weather Code Mapping

The API returns WMO (World Meteorological Organization) weather codes. Our pipeline maps these to human-readable descriptions.

### Code Mapping Table

| Code | Description | Category |
|------|-------------|----------|
| 0    | Clear sky   | Clear |
| 1    | Mainly clear | Clear |
| 2    | Partly cloudy | Cloudy |
| 3    | Overcast | Cloudy |
| 45   | Foggy | Fog |
| 48   | Depositing rime fog | Fog |
| 51   | Light drizzle | Drizzle |
| 53   | Moderate drizzle | Drizzle |
| 55   | Dense drizzle | Drizzle |
| 61   | Slight rain | Rain |
| 63   | Moderate rain | Rain |
| 65   | Heavy rain | Rain |
| 71   | Slight snow | Snow |
| 73   | Moderate snow | Snow |
| 75   | Heavy snow | Snow |
| 77   | Snow grains | Snow |
| 80   | Slight rain showers | Rain |
| 81   | Moderate rain showers | Rain |
| 82   | Violent rain showers | Rain |
| 85   | Slight snow showers | Snow |
| 86   | Heavy snow showers | Snow |
| 95   | Thunderstorm | Storm |
| 96   | Thunderstorm with slight hail | Storm |
| 99   | Thunderstorm with heavy hail | Storm |

### Implementation

```python
def get_weather_description(code: int) -> str:
    """Convert WMO weather code to description"""
    weather_codes = {
        0: 'Clear sky',
        1: 'Mainly clear',
        2: 'Partly cloudy',
        3: 'Overcast',
        # ... more mappings
    }
    return weather_codes.get(code, f'Unknown ({code})')
```

## Error Handling

### Common Errors

1. **Network Timeout**
   ```python
   try:
       response = requests.get(url, params=params, timeout=10)
   except requests.exceptions.Timeout:
       # Retry with exponential backoff
       pass
   ```

2. **Invalid Coordinates**
   - Latitude out of range (-90 to 90)
   - Longitude out of range (-180 to 180)
   - API returns 400 Bad Request

3. **API Unavailable**
   - 500 Server Error
   - Service temporarily down
   - Implement retry logic

4. **Rate Limiting** (unlikely but possible)
   - Add delays between requests
   - Implement exponential backoff

### Retry Strategy

```python
@task(retries=3, retry_delay=timedelta(minutes=2))
def extract_weather_for_city(city_info):
    try:
        return call_open_meteo_api(city_info)
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {city_info['name']}: {e}")
        raise  # Trigger Airflow retry
```

## API Limitations and Best Practices

### Rate Limits

- **Official Limit**: No strict rate limit for fair use
- **Recommended**: < 10,000 requests per day
- **Our Usage**: ~10 cities × daily = 10 requests/day (well within limit)

### Best Practices

1. **Timeout Settings**
   ```python
   response = requests.get(url, params=params, timeout=10)
   ```

2. **Error Handling**
   ```python
   response.raise_for_status()  # Raise exception for 4xx/5xx
   ```

3. **Logging**
   ```python
   logger.info(f"API request for {city}: {url}?{params}")
   logger.info(f"API response: {response.status_code}")
   ```

4. **Caching** (optional)
   - Cache responses for development
   - Avoid unnecessary API calls

## Example Usage

### Fetch Weather for Single City

```python
import requests

def fetch_weather(city_name, latitude, longitude):
    """Fetch current weather for a city"""
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
        'timezone': 'auto'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        
        return {
            'city': city_name,
            'temperature_celsius': current['temperature_2m'],
            'humidity': current['relative_humidity_2m'],
            'wind_speed': current['wind_speed_10m'],
            'weather_code': current['weather_code'],
            'timestamp': current['time']
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather for {city_name}: {e}")
        raise

# Example
weather = fetch_weather("New York", 40.7128, -74.0060)
print(f"Temperature in {weather['city']}: {weather['temperature_celsius']}°C")
```

### Fetch Weather for Multiple Cities

```python
cities = [
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503}
]

weather_data = []

for city in cities:
    try:
        weather = fetch_weather(city['name'], city['lat'], city['lon'])
        weather_data.append(weather)
        print(f"✓ Fetched weather for {city['name']}")
    except Exception as e:
        print(f"✗ Failed to fetch weather for {city['name']}: {e}")

print(f"\nSuccessfully fetched weather for {len(weather_data)}/{len(cities)} cities")
```

## Advanced Features

### Historical Data

```python
params = {
    'latitude': 40.7128,
    'longitude': -74.0060,
    'start_date': '2024-01-01',
    'end_date': '2024-01-07',
    'daily': 'temperature_2m_max,temperature_2m_min',
    'timezone': 'auto'
}
```

### Hourly Forecast

```python
params = {
    'latitude': 40.7128,
    'longitude': -74.0060,
    'hourly': 'temperature_2m,precipitation',
    'forecast_days': 7,
    'timezone': 'auto'
}
```

### Additional Variables

Available variables (see full API documentation):
- `precipitation`
- `rain`
- `snowfall`
- `cloud_cover`
- `pressure_msl`
- `surface_pressure`
- `visibility`
- `wind_direction_10m`
- `wind_gusts_10m`
- And many more...

## Testing the API

### Manual Test with curl

```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto"
```

### Python Test Script

```python
#!/usr/bin/env python3
"""Test Open-Meteo API connection"""

import requests
import json

def test_api():
    """Test API connection and response"""
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': 40.7128,
        'longitude': -74.0060,
        'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
        'timezone': 'auto'
    }
    
    print("Testing Open-Meteo API...")
    print(f"URL: {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print("\n[SUCCESS] API Request Successful!")
        print(f"\nResponse:")
        print(json.dumps(data, indent=2))
        
        current = data['current']
        print(f"\nCurrent Weather:")
        print(f"  Temperature: {current['temperature_2m']}°C")
        print(f"  Humidity: {current['relative_humidity_2m']}%")
        print(f"  Wind Speed: {current['wind_speed_10m']} m/s")
        print(f"  Weather Code: {current['weather_code']}")
        print(f"  Time: {current['time']}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_api()
```

## Resources

- **Official Documentation**: https://open-meteo.com/en/docs
- **API Playground**: https://open-meteo.com/en/docs#api_form
- **GitHub**: https://github.com/open-meteo/open-meteo
- **Terms of Use**: https://open-meteo.com/en/terms

## License and Attribution

Open-Meteo is open-source and free to use under the Attribution 4.0 International (CC BY 4.0) license.

**Attribution**:
```
Weather data by Open-Meteo.com
https://open-meteo.com/
```

Include this attribution in any public-facing applications using this data.