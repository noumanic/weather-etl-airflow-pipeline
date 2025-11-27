"""
Unit tests for Load functions
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add dags directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))

from helpers import load_weather_records_to_db, load_daily_stats_to_db, validate_loaded_data


class TestLoad:
    """Test cases for weather data loading"""
    
    def test_load_weather_records_success(self):
        """Test successful loading of weather records"""
        weather_data = [
            {
                'city': 'Test City',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'temperature_celsius': 20.0,
                'temperature_fahrenheit': 68.0,
                'humidity': 60,
                'wind_speed': 5.0,
                'weather_condition': 'Clear sky',
                'timestamp': '2024-01-01T12:00:00',
                'extraction_date': '2024-01-01T13:00:00'
            }
        ]
        
        # Mock PostgresHook
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_weather_records_to_db(weather_data, mock_hook)
        
        assert result == 1
        assert mock_cursor.execute.called
        assert mock_conn.commit.called
    
    def test_load_weather_records_empty_list(self):
        """Test loading empty weather records list"""
        mock_hook = Mock()
        
        result = load_weather_records_to_db([], mock_hook)
        
        assert result == 0
    
    def test_load_weather_records_multiple(self):
        """Test loading multiple weather records"""
        weather_data = [
            {
                'city': f'City {i}',
                'latitude': 40.0 + i,
                'longitude': -74.0 + i,
                'temperature_celsius': 20.0 + i,
                'temperature_fahrenheit': 68.0 + i,
                'humidity': 60,
                'wind_speed': 5.0,
                'weather_condition': 'Clear sky',
                'timestamp': '2024-01-01T12:00:00',
                'extraction_date': '2024-01-01T13:00:00'
            }
            for i in range(5)
        ]
        
        # Mock PostgresHook
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_weather_records_to_db(weather_data, mock_hook)
        
        assert result == 5
        assert mock_cursor.execute.call_count == 5
    
    def test_load_daily_stats_success(self):
        """Test successful loading of daily statistics"""
        daily_stats = {
            'date': '2024-01-01',
            'avg_temp_celsius': 20.0,
            'avg_temp_fahrenheit': 68.0,
            'max_temp_celsius': 25.0,
            'max_temp_fahrenheit': 77.0,
            'min_temp_celsius': 15.0,
            'min_temp_fahrenheit': 59.0,
            'avg_humidity': 60.0,
            'avg_wind_speed': 5.0,
            'cities': ['City 1', 'City 2']
        }
        
        # Mock PostgresHook
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_daily_stats_to_db(daily_stats, mock_hook)
        
        assert result == 2  # 2 cities
        assert mock_cursor.execute.call_count == 2
        assert mock_conn.commit.called
    
    def test_load_daily_stats_empty(self):
        """Test loading empty daily statistics"""
        mock_hook = Mock()
        
        result = load_daily_stats_to_db({}, mock_hook)
        
        assert result == 0
    
    def test_validate_loaded_data_all_passed(self):
        """Test data validation when all checks pass"""
        # Mock PostgresHook
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock query results (all checks pass)
        mock_cursor.fetchone.side_effect = [
            (10,),  # today_count
            (0,),   # null_temp_count
            (0,),   # invalid_temp_count
            (0,),   # conversion_error_count
            (0,),   # invalid_humidity_count
            (3,)    # stats_count
        ]
        
        passed, messages = validate_loaded_data(mock_hook)
        
        assert passed is True
        assert len(messages) == 6
    
    def test_validate_loaded_data_no_records(self):
        """Test data validation when no records found"""
        # Mock PostgresHook
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock query results (no records)
        mock_cursor.fetchone.side_effect = [
            (0,),   # today_count
            (0,),   # null_temp_count
            (0,),   # invalid_temp_count
            (0,),   # conversion_error_count
            (0,),   # invalid_humidity_count
            (0,)    # stats_count
        ]
        
        passed, messages = validate_loaded_data(mock_hook)
        
        assert passed is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
