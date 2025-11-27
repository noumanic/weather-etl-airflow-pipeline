"""
Helper functions for Weather ETL Pipeline
Provides reusable functions for API calls, transformations, and database operations.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
import logging
import requests
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


def call_open_meteo_api(city_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call Open-Meteo API to fetch weather data for a city
    
    Args:
        city_info: Dictionary containing city name, latitude, and longitude
    
    Returns:
        Dictionary containing weather data
    
    Raises:
        requests.exceptions.RequestException: If API call fails
    """
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': city_info['latitude'],
        'longitude': city_info['longitude'],
        'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
        'timezone': 'auto'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract current weather data
        current = data.get('current', {})
        
        # Map weather code to description (simplified)
        weather_code = current.get('weather_code', 0)
        weather_condition = get_weather_description(weather_code)
        
        # Build weather record
        weather_record = {
            'city': city_info['name'],
            'latitude': city_info['latitude'],
            'longitude': city_info['longitude'],
            'temperature_celsius': current.get('temperature_2m'),
            'humidity': current.get('relative_humidity_2m'),
            'wind_speed': current.get('wind_speed_10m'),
            'weather_condition': weather_condition,
            'timestamp': current.get('time')
        }
        
        return weather_record
        
    except requests.exceptions.Timeout:
        logger.error(f"API request timeout for {city_info['name']}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {city_info['name']}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling API for {city_info['name']}: {str(e)}")
        raise


def get_weather_description(code: int) -> str:
    """
    Convert WMO weather code to human-readable description
    
    Args:
        code: WMO weather code
    
    Returns:
        Weather description string
    """
    weather_codes = {
        0: 'Clear sky',
        1: 'Mainly clear',
        2: 'Partly cloudy',
        3: 'Overcast',
        45: 'Foggy',
        48: 'Depositing rime fog',
        51: 'Light drizzle',
        53: 'Moderate drizzle',
        55: 'Dense drizzle',
        61: 'Slight rain',
        63: 'Moderate rain',
        65: 'Heavy rain',
        71: 'Slight snow',
        73: 'Moderate snow',
        75: 'Heavy snow',
        77: 'Snow grains',
        80: 'Slight rain showers',
        81: 'Moderate rain showers',
        82: 'Violent rain showers',
        85: 'Slight snow showers',
        86: 'Heavy snow showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with slight hail',
        99: 'Thunderstorm with heavy hail'
    }
    
    return weather_codes.get(code, f'Unknown ({code})')


def to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit
    
    Args:
        celsius: Temperature in Celsius
    
    Returns:
        Temperature in Fahrenheit rounded to 2 decimal places
    """
    if celsius is None:
        return None
    
    fahrenheit = (celsius * 9/5) + 32
    return round(fahrenheit, 2)


def add_extraction_timestamp(weather_data: Dict[str, Any], extraction_time: datetime) -> None:
    """
    Add extraction timestamp to weather data (modifies dict in place)
    
    Args:
        weather_data: Weather data dictionary
        extraction_time: Timestamp of data extraction
    """
    weather_data['extraction_date'] = extraction_time.isoformat()
    
    # Ensure timestamp is properly formatted
    if isinstance(weather_data.get('timestamp'), str):
        # Already a string, keep it
        pass
    elif isinstance(weather_data.get('timestamp'), datetime):
        weather_data['timestamp'] = weather_data['timestamp'].isoformat()


def calculate_daily_statistics(weather_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate daily statistics from weather data
    
    Args:
        weather_data_list: List of weather data dictionaries
    
    Returns:
        Dictionary containing daily statistics
    """
    if not weather_data_list:
        return {}
    
    # Extract temperatures
    temps_celsius = [w['temperature_celsius'] for w in weather_data_list if w.get('temperature_celsius') is not None]
    temps_fahrenheit = [w['temperature_fahrenheit'] for w in weather_data_list if w.get('temperature_fahrenheit') is not None]
    humidities = [w['humidity'] for w in weather_data_list if w.get('humidity') is not None]
    wind_speeds = [w['wind_speed'] for w in weather_data_list if w.get('wind_speed') is not None]
    
    # Calculate statistics
    stats = {
        'date': datetime.now(timezone.utc).date().isoformat(),
        'avg_temp_celsius': round(sum(temps_celsius) / len(temps_celsius), 2) if temps_celsius else None,
        'avg_temp_fahrenheit': round(sum(temps_fahrenheit) / len(temps_fahrenheit), 2) if temps_fahrenheit else None,
        'max_temp_celsius': round(max(temps_celsius), 2) if temps_celsius else None,
        'max_temp_fahrenheit': round(max(temps_fahrenheit), 2) if temps_fahrenheit else None,
        'min_temp_celsius': round(min(temps_celsius), 2) if temps_celsius else None,
        'min_temp_fahrenheit': round(min(temps_fahrenheit), 2) if temps_fahrenheit else None,
        'avg_humidity': round(sum(humidities) / len(humidities), 2) if humidities else None,
        'avg_wind_speed': round(sum(wind_speeds) / len(wind_speeds), 2) if wind_speeds else None,
        'cities_count': len(weather_data_list),
        'cities': [w['city'] for w in weather_data_list]
    }
    
    return stats


def load_weather_records_to_db(weather_data_list: List[Dict[str, Any]], pg_hook: PostgresHook) -> int:
    """
    Load weather records into PostgreSQL database
    
    Args:
        weather_data_list: List of weather data dictionaries
        pg_hook: PostgreSQL hook for database connection
    
    Returns:
        Number of records inserted
    """
    if not weather_data_list:
        logger.warning("No weather data to load")
        return 0
    
    insert_sql = """
        INSERT INTO weather_records (
            city, latitude, longitude, 
            temperature_celsius, temperature_fahrenheit,
            humidity, wind_speed, weather_condition,
            timestamp, extraction_date
        ) VALUES (
            %(city)s, %(latitude)s, %(longitude)s,
            %(temperature_celsius)s, %(temperature_fahrenheit)s,
            %(humidity)s, %(wind_speed)s, %(weather_condition)s,
            %(timestamp)s, %(extraction_date)s
        )
    """
    
    try:
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        records_inserted = 0
        for weather in weather_data_list:
            try:
                cursor.execute(insert_sql, weather)
                records_inserted += 1
                logger.info(f"Inserted weather record for {weather['city']}")
            except Exception as e:
                logger.error(f"Failed to insert record for {weather.get('city', 'Unknown')}: {str(e)}")
                conn.rollback()
                raise
        
        conn.commit()
        cursor.close()
        
        logger.info(f"Successfully loaded {records_inserted} weather records")
        return records_inserted
        
    except Exception as e:
        logger.error(f"Database error while loading weather records: {str(e)}")
        raise


def load_daily_stats_to_db(daily_stats: Dict[str, Any], pg_hook: PostgresHook) -> int:
    """
    Load daily statistics into PostgreSQL database
    
    Args:
        daily_stats: Dictionary containing daily statistics
        pg_hook: PostgreSQL hook for database connection
    
    Returns:
        Number of statistics records inserted
    """
    if not daily_stats or 'cities' not in daily_stats:
        logger.warning("No daily statistics to load")
        return 0
    
    insert_sql = """
        INSERT INTO daily_weather_stats (
            city, date,
            avg_temp_celsius, avg_temp_fahrenheit,
            max_temp_celsius, max_temp_fahrenheit,
            min_temp_celsius, min_temp_fahrenheit,
            avg_humidity, avg_wind_speed
        ) VALUES (
            %(city)s, %(date)s,
            %(avg_temp_celsius)s, %(avg_temp_fahrenheit)s,
            %(max_temp_celsius)s, %(max_temp_fahrenheit)s,
            %(min_temp_celsius)s, %(min_temp_fahrenheit)s,
            %(avg_humidity)s, %(avg_wind_speed)s
        )
        ON CONFLICT (city, date) 
        DO UPDATE SET
            avg_temp_celsius = EXCLUDED.avg_temp_celsius,
            avg_temp_fahrenheit = EXCLUDED.avg_temp_fahrenheit,
            max_temp_celsius = EXCLUDED.max_temp_celsius,
            max_temp_fahrenheit = EXCLUDED.max_temp_fahrenheit,
            min_temp_celsius = EXCLUDED.min_temp_celsius,
            min_temp_fahrenheit = EXCLUDED.min_temp_fahrenheit,
            avg_humidity = EXCLUDED.avg_humidity,
            avg_wind_speed = EXCLUDED.avg_wind_speed,
            created_at = CURRENT_TIMESTAMP
    """
    
    try:
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        stats_inserted = 0
        # Insert stats for each city
        for city in daily_stats['cities']:
            stat_record = {
                'city': city,
                'date': daily_stats['date'],
                'avg_temp_celsius': daily_stats['avg_temp_celsius'],
                'avg_temp_fahrenheit': daily_stats['avg_temp_fahrenheit'],
                'max_temp_celsius': daily_stats['max_temp_celsius'],
                'max_temp_fahrenheit': daily_stats['max_temp_fahrenheit'],
                'min_temp_celsius': daily_stats['min_temp_celsius'],
                'min_temp_fahrenheit': daily_stats['min_temp_fahrenheit'],
                'avg_humidity': daily_stats['avg_humidity'],
                'avg_wind_speed': daily_stats['avg_wind_speed']
            }
            
            try:
                cursor.execute(insert_sql, stat_record)
                stats_inserted += 1
                logger.info(f"Inserted daily statistics for {city}")
            except Exception as e:
                logger.error(f"Failed to insert statistics for {city}: {str(e)}")
                conn.rollback()
                raise
        
        conn.commit()
        cursor.close()
        
        logger.info(f"Successfully loaded {stats_inserted} daily statistics records")
        return stats_inserted
        
    except Exception as e:
        logger.error(f"Database error while loading daily statistics: {str(e)}")
        raise


def validate_loaded_data(pg_hook: PostgresHook) -> Tuple[bool, List[str]]:
    """
    Perform data quality checks on loaded data
    
    Args:
        pg_hook: PostgreSQL hook for database connection
    
    Returns:
        Tuple of (passed: bool, messages: List[str])
    """
    messages = []
    all_passed = True
    
    try:
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        # Check 1: Verify records were inserted today
        cursor.execute("""
            SELECT COUNT(*) FROM weather_records 
            WHERE DATE(extraction_date) = CURRENT_DATE
        """)
        today_count = cursor.fetchone()[0]
        
        if today_count == 0:
            messages.append("[FAIL] No records inserted today")
            all_passed = False
        else:
            messages.append(f"[OK] Found {today_count} records inserted today")
        
        # Check 2: Check for NULL temperatures
        cursor.execute("""
            SELECT COUNT(*) FROM weather_records 
            WHERE temperature_celsius IS NULL 
            AND DATE(extraction_date) = CURRENT_DATE
        """)
        null_temp_count = cursor.fetchone()[0]
        
        if null_temp_count > 0:
            messages.append(f"⚠ Warning: {null_temp_count} records with NULL temperature")
        else:
            messages.append("[OK] No NULL temperatures found")
        
        # Check 3: Validate temperature ranges (-50°C to 60°C)
        cursor.execute("""
            SELECT COUNT(*) FROM weather_records 
            WHERE temperature_celsius < -50 OR temperature_celsius > 60
            AND DATE(extraction_date) = CURRENT_DATE
        """)
        invalid_temp_count = cursor.fetchone()[0]
        
        if invalid_temp_count > 0:
            messages.append(f"⚠ Warning: {invalid_temp_count} records with invalid temperature range")
        else:
            messages.append("[OK] All temperatures within valid range")
        
        # Check 4: Validate Celsius to Fahrenheit conversion
        cursor.execute("""
            SELECT COUNT(*) FROM weather_records 
            WHERE ABS(temperature_fahrenheit - (temperature_celsius * 9/5 + 32)) > 0.1
            AND DATE(extraction_date) = CURRENT_DATE
        """)
        conversion_error_count = cursor.fetchone()[0]
        
        if conversion_error_count > 0:
            messages.append(f"[FAIL] {conversion_error_count} records with incorrect temperature conversion")
            all_passed = False
        else:
            messages.append("[OK] Temperature conversions are correct")
        
        # Check 5: Verify humidity range (0-100%)
        cursor.execute("""
            SELECT COUNT(*) FROM weather_records 
            WHERE humidity < 0 OR humidity > 100
            AND DATE(extraction_date) = CURRENT_DATE
        """)
        invalid_humidity_count = cursor.fetchone()[0]
        
        if invalid_humidity_count > 0:
            messages.append(f"⚠ Warning: {invalid_humidity_count} records with invalid humidity")
        else:
            messages.append("[OK] All humidity values within valid range")
        
        # Check 6: Verify daily statistics exist
        cursor.execute("""
            SELECT COUNT(*) FROM daily_weather_stats 
            WHERE date = CURRENT_DATE
        """)
        stats_count = cursor.fetchone()[0]
        
        if stats_count == 0:
            messages.append("[FAIL] No daily statistics found for today")
            all_passed = False
        else:
            messages.append(f"[OK] Found {stats_count} daily statistics records")
        
        cursor.close()
        
        # Log all messages
        for msg in messages:
            logger.info(msg)
        
        return all_passed, messages
        
    except Exception as e:
        logger.error(f"Error during data validation: {str(e)}")
        messages.append(f"[ERROR] Validation error: {str(e)}")
        return False, messages