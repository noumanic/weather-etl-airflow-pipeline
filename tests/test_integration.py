"""
Integration tests for Weather ETL Pipeline
Tests the entire pipeline flow
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import sys
import os

# Add dags directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))

from helpers import (
    call_open_meteo_api,
    to_fahrenheit,
    add_extraction_timestamp,
    calculate_daily_statistics,
    load_weather_records_to_db,
    load_daily_stats_to_db,
    validate_loaded_data
)


class TestIntegration:
    """Integration test cases for the complete ETL pipeline"""
    
    @pytest.fixture
    def sample_cities(self):
        """Sample cities for testing"""
        return [
            {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
            {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
            {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503}
        ]
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response"""
        def create_response(city_info):
            mock_response = Mock()
            mock_response.json.return_value = {
                'current': {
                    'temperature_2m': 20.5,
                    'relative_humidity_2m': 65,
                    'wind_speed_10m': 5.2,
                    'weather_code': 0,
                    'time': '2024-01-01T12:00:00'
                }
            }
            mock_response.raise_for_status = Mock()
            return mock_response
        return create_response
    
    def test_complete_etl_pipeline(self, sample_cities, mock_api_response):
        """Test complete ETL pipeline flow: Extract -> Transform -> Load"""
        
        # 1. EXTRACT: Mock API calls
        extracted_data = []
        with patch('requests.get') as mock_get:
            for city in sample_cities:
                mock_get.return_value = mock_api_response(city)
                weather_record = call_open_meteo_api(city)
                extracted_data.append(weather_record)
        
        assert len(extracted_data) == 3
        assert all('temperature_celsius' in record for record in extracted_data)
        
        # 2. TRANSFORM: Convert temperatures
        for record in extracted_data:
            record['temperature_fahrenheit'] = to_fahrenheit(record['temperature_celsius'])
        
        assert all('temperature_fahrenheit' in record for record in extracted_data)
        assert all(record['temperature_fahrenheit'] == 68.9 for record in extracted_data)
        
        # 3. TRANSFORM: Add timestamps
        extraction_time = datetime.now(timezone.utc)
        for record in extracted_data:
            add_extraction_timestamp(record, extraction_time)
        
        assert all('extraction_date' in record for record in extracted_data)
        
        # 4. TRANSFORM: Calculate statistics
        stats = calculate_daily_statistics(extracted_data)
        
        assert stats is not None
        assert 'avg_temp_celsius' in stats
        assert 'cities' in stats
        assert len(stats['cities']) == 3
        
        # 5. LOAD: Mock database loading
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        records_loaded = load_weather_records_to_db(extracted_data, mock_hook)
        stats_loaded = load_daily_stats_to_db(stats, mock_hook)
        
        assert records_loaded == 3
        assert stats_loaded == 3
    
    def test_etl_pipeline_with_errors(self, sample_cities):
        """Test ETL pipeline behavior with API errors"""
        
        # Test extraction with API timeout
        with patch('requests.get', side_effect=Exception("Network error")):
            with pytest.raises(Exception):
                call_open_meteo_api(sample_cities[0])
    
    def test_etl_pipeline_data_quality(self, sample_cities, mock_api_response):
        """Test data quality validation in pipeline"""
        
        # Extract and transform data
        extracted_data = []
        with patch('requests.get') as mock_get:
            for city in sample_cities:
                mock_get.return_value = mock_api_response(city)
                weather_record = call_open_meteo_api(city)
                weather_record['temperature_fahrenheit'] = to_fahrenheit(
                    weather_record['temperature_celsius']
                )
                extracted_data.append(weather_record)
        
        # Verify temperature conversion accuracy
        for record in extracted_data:
            celsius = record['temperature_celsius']
            fahrenheit = record['temperature_fahrenheit']
            expected_fahrenheit = (celsius * 9/5) + 32
            assert abs(fahrenheit - expected_fahrenheit) < 0.1
        
        # Verify data completeness
        required_fields = [
            'city', 'latitude', 'longitude', 'temperature_celsius',
            'temperature_fahrenheit', 'humidity', 'wind_speed', 'weather_condition'
        ]
        
        for record in extracted_data:
            for field in required_fields:
                assert field in record
    
    def test_etl_pipeline_idempotency(self, sample_cities, mock_api_response):
        """Test that running pipeline multiple times produces consistent results"""
        
        results = []
        
        for run in range(2):
            extracted_data = []
            with patch('requests.get') as mock_get:
                for city in sample_cities:
                    mock_get.return_value = mock_api_response(city)
                    weather_record = call_open_meteo_api(city)
                    weather_record['temperature_fahrenheit'] = to_fahrenheit(
                        weather_record['temperature_celsius']
                    )
                    extracted_data.append(weather_record)
            
            stats = calculate_daily_statistics(extracted_data)
            results.append(stats)
        
        # Verify statistics are consistent across runs
        assert results[0]['avg_temp_celsius'] == results[1]['avg_temp_celsius']
        assert results[0]['avg_temp_fahrenheit'] == results[1]['avg_temp_fahrenheit']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
