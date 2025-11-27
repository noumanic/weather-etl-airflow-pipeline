"""
Unit tests for Transform functions
"""

import pytest
from datetime import datetime, timezone
import sys
import os

# Add dags directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))

from helpers import to_fahrenheit, add_extraction_timestamp, calculate_daily_statistics


class TestTransform:
    """Test cases for weather data transformation"""
    
    def test_to_fahrenheit_zero(self):
        """Test Celsius to Fahrenheit conversion for 0°C"""
        result = to_fahrenheit(0)
        assert result == 32.0
    
    def test_to_fahrenheit_positive(self):
        """Test Celsius to Fahrenheit conversion for positive temperature"""
        result = to_fahrenheit(20)
        assert result == 68.0
    
    def test_to_fahrenheit_negative(self):
        """Test Celsius to Fahrenheit conversion for negative temperature"""
        result = to_fahrenheit(-10)
        assert result == 14.0
    
    def test_to_fahrenheit_decimal(self):
        """Test Celsius to Fahrenheit conversion for decimal temperature"""
        result = to_fahrenheit(25.5)
        assert result == 77.9
    
    def test_to_fahrenheit_none(self):
        """Test Celsius to Fahrenheit conversion for None"""
        result = to_fahrenheit(None)
        assert result is None
    
    def test_add_extraction_timestamp(self):
        """Test adding extraction timestamp to weather data"""
        weather_data = {
            'city': 'Test City',
            'temperature_celsius': 20.0,
            'timestamp': '2024-01-01T12:00:00'
        }
        extraction_time = datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
        
        add_extraction_timestamp(weather_data, extraction_time)
        
        assert 'extraction_date' in weather_data
        assert weather_data['extraction_date'] == '2024-01-01T13:00:00+00:00'
    
    def test_add_extraction_timestamp_datetime(self):
        """Test adding extraction timestamp when timestamp is datetime"""
        weather_data = {
            'city': 'Test City',
            'temperature_celsius': 20.0,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        }
        extraction_time = datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
        
        add_extraction_timestamp(weather_data, extraction_time)
        
        assert 'extraction_date' in weather_data
        assert isinstance(weather_data['timestamp'], str)
    
    def test_calculate_daily_statistics_single_city(self):
        """Test calculating daily statistics for single city"""
        weather_data = [
            {
                'city': 'Test City',
                'temperature_celsius': 20.0,
                'temperature_fahrenheit': 68.0,
                'humidity': 60,
                'wind_speed': 5.0
            }
        ]
        
        stats = calculate_daily_statistics(weather_data)
        
        assert stats['avg_temp_celsius'] == 20.0
        assert stats['avg_temp_fahrenheit'] == 68.0
        assert stats['max_temp_celsius'] == 20.0
        assert stats['min_temp_celsius'] == 20.0
        assert stats['avg_humidity'] == 60
        assert stats['avg_wind_speed'] == 5.0
        assert stats['cities_count'] == 1
        assert 'Test City' in stats['cities']
    
    def test_calculate_daily_statistics_multiple_cities(self):
        """Test calculating daily statistics for multiple cities"""
        weather_data = [
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
        
        stats = calculate_daily_statistics(weather_data)
        
        assert stats['avg_temp_celsius'] == 20.0
        assert stats['max_temp_celsius'] == 30.0
        assert stats['min_temp_celsius'] == 10.0
        assert stats['avg_humidity'] == 60.0
        assert stats['cities_count'] == 3
    
    def test_calculate_daily_statistics_empty_list(self):
        """Test calculating daily statistics for empty list"""
        stats = calculate_daily_statistics([])
        assert stats == {}
    
    def test_calculate_daily_statistics_with_none_values(self):
        """Test calculating daily statistics with None values"""
        weather_data = [
            {
                'city': 'City 1',
                'temperature_celsius': 20.0,
                'temperature_fahrenheit': 68.0,
                'humidity': 60,
                'wind_speed': 5.0
            },
            {
                'city': 'City 2',
                'temperature_celsius': None,
                'temperature_fahrenheit': None,
                'humidity': None,
                'wind_speed': None
            }
        ]
        
        stats = calculate_daily_statistics(weather_data)
        
        # Should only include non-None values in calculations
        assert stats['avg_temp_celsius'] == 20.0
        assert stats['cities_count'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
