#!/usr/bin/env python3
"""
Test Components Script
Standalone script to test individual components of the ETL pipeline
"""

import sys
import os
import requests
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dags.helpers import (
    call_open_meteo_api,
    to_fahrenheit,
    add_extraction_timestamp,
    calculate_daily_statistics,
    get_weather_description
)


def test_api_connection():
    """Test API connection with sample city"""
    print("\n" + "="*60)
    print("Testing API Connection")
    print("="*60)
    
    test_city = {
        "name": "New York",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    try:
        print(f"\nFetching weather data for {test_city['name']}...")
        weather_data = call_open_meteo_api(test_city)
        
        print("\n[SUCCESS] API connection successful!")
        print(f"\nWeather Data Retrieved:")
        print(f"  City: {weather_data['city']}")
        print(f"  Temperature: {weather_data['temperature_celsius']}°C")
        print(f"  Humidity: {weather_data['humidity']}%")
        print(f"  Wind Speed: {weather_data['wind_speed']} m/s")
        print(f"  Condition: {weather_data['weather_condition']}")
        print(f"  Timestamp: {weather_data['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] API connection failed: {str(e)}")
        return False


def test_temperature_conversion():
    """Test temperature conversion functions"""
    print("\n" + "="*60)
    print("Testing Temperature Conversion")
    print("="*60)
    
    test_cases = [
        (0, 32.0),
        (100, 212.0),
        (-40, -40.0),
        (20, 68.0),
        (25.5, 77.9)
    ]
    
    all_passed = True
    
    for celsius, expected_fahrenheit in test_cases:
        result = to_fahrenheit(celsius)
        passed = abs(result - expected_fahrenheit) < 0.1
        
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {celsius}°C = {result}°F (expected {expected_fahrenheit}°F)")
        
        if not passed:
            all_passed = False
    
    # Test None case
    result = to_fahrenheit(None)
    if result is None:
        print(f"[PASS] None input handled correctly")
    else:
        print(f"[FAIL] None input not handled correctly")
        all_passed = False
    
    return all_passed


def test_daily_statistics():
    """Test daily statistics calculation"""
    print("\n" + "="*60)
    print("Testing Daily Statistics Calculation")
    print("="*60)
    
    sample_data = [
        {
            'city': 'City 1',
            'temperature_celsius': 10.0,
            'temperature_fahrenheit': 50.0,
            'humidity': 50,
            'wind_speed': 3.0
        },
        {
            'city': 'City 2',
            'temperature_celsius': 20.0,
            'temperature_fahrenheit': 68.0,
            'humidity': 70,
            'wind_speed': 5.0
        },
        {
            'city': 'City 3',
            'temperature_celsius': 30.0,
            'temperature_fahrenheit': 86.0,
            'humidity': 60,
            'wind_speed': 4.0
        }
    ]
    
    try:
        stats = calculate_daily_statistics(sample_data)
        
        print(f"\n[SUCCESS] Statistics calculated successfully!")
        print(f"\nStatistics:")
        print(f"  Average Temperature: {stats['avg_temp_celsius']}°C / {stats['avg_temp_fahrenheit']}°F")
        print(f"  Max Temperature: {stats['max_temp_celsius']}°C / {stats['max_temp_fahrenheit']}°F")
        print(f"  Min Temperature: {stats['min_temp_celsius']}°C / {stats['min_temp_fahrenheit']}°F")
        print(f"  Average Humidity: {stats['avg_humidity']}%")
        print(f"  Average Wind Speed: {stats['avg_wind_speed']} m/s")
        print(f"  Cities Count: {stats['cities_count']}")
        print(f"  Cities: {', '.join(stats['cities'])}")
        
        # Verify calculations
        expected_avg = 20.0
        if abs(stats['avg_temp_celsius'] - expected_avg) < 0.1:
            print(f"\n[PASS] Average calculation verified (20.0°C)")
            return True
        else:
            print(f"\n[FAIL] Average calculation incorrect")
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Statistics calculation failed: {str(e)}")
        return False


def test_timestamp_functions():
    """Test timestamp manipulation"""
    print("\n" + "="*60)
    print("Testing Timestamp Functions")
    print("="*60)
    
    weather_data = {
        'city': 'Test City',
        'temperature_celsius': 20.0,
        'timestamp': '2024-01-01T12:00:00'
    }
    
    extraction_time = datetime.now(timezone.utc)
    
    try:
        add_extraction_timestamp(weather_data, extraction_time)
        
        print(f"\n[SUCCESS] Timestamp added successfully!")
        print(f"  Original Timestamp: {weather_data['timestamp']}")
        print(f"  Extraction Date: {weather_data['extraction_date']}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Timestamp manipulation failed: {str(e)}")
        return False


def test_weather_descriptions():
    """Test weather code descriptions"""
    print("\n" + "="*60)
    print("Testing Weather Code Descriptions")
    print("="*60)
    
    test_codes = [
        (0, 'Clear sky'),
        (61, 'Slight rain'),
        (71, 'Slight snow'),
        (95, 'Thunderstorm')
    ]
    
    all_passed = True
    
    for code, expected in test_codes:
        result = get_weather_description(code)
        passed = result == expected
        
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} Code {code}: {result}")
        
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    """Run all component tests"""
    print("\n" + "="*60)
    print("Weather ETL Pipeline - Component Testing")
    print("="*60)
    print(f"Test Run Time: {datetime.now()}")
    
    results = {
        "API Connection": test_api_connection(),
        "Temperature Conversion": test_temperature_conversion(),
        "Daily Statistics": test_daily_statistics(),
        "Timestamp Functions": test_timestamp_functions(),
        "Weather Descriptions": test_weather_descriptions()
    }
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "[PASS] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\n{'='*60}")
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print(f"{'='*60}\n")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
