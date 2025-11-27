"""
Weather ETL Pipeline DAG
This DAG extracts weather data from Open-Meteo API, transforms it, and loads into PostgreSQL.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
import logging

from airflow.decorators import dag, task, task_group
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests

# Import helper functions
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from helpers import (
    call_open_meteo_api,
    to_fahrenheit,
    add_extraction_timestamp,
    calculate_daily_statistics as calc_daily_stats,
    load_weather_records_to_db,
    load_daily_stats_to_db,
    validate_loaded_data
)


# Configure logging
logger = logging.getLogger(__name__)


# City coordinates for weather data extraction
# Load cities config from project config
try:
    from config.cities import CITIES
except Exception:
    # Fallback: small list
    CITIES = [
        {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
        {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
        {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    ]


# Default arguments for the DAG
default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='weather_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for weather data collection and storage',
    schedule_interval='@daily',  # Run daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['weather', 'etl', 'mlops'],
)
def weather_etl_pipeline():
    """
    Main Weather ETL Pipeline DAG
    
    This DAG performs the following operations:
    1. Extract: Fetch weather data from Open-Meteo API for multiple cities
    2. Transform: Convert temperatures and calculate statistics
    3. Load: Insert data into PostgreSQL
    4. Validate: Perform data quality checks
    5. Notify: Send completion notification
    """
    
    # =====================
    # EXTRACT TASK GROUP
    # =====================
    @task_group(group_id='extract_weather_data')
    def extract_group():
        """Task group for extracting weather data from API"""
        
        @task(retries=3, retry_delay=timedelta(minutes=2))
        def extract_weather_for_city(city_info: Dict[str, Any]) -> Dict[str, Any]:
            """
            Extract weather data for a single city from Open-Meteo API
            
            Args:
                city_info: Dictionary containing city name, latitude, and longitude
            
            Returns:
                Dictionary containing weather data
            """
            try:
                logger.info(f"Extracting weather data for {city_info['name']}")
                # Delegate to helper which is easily testable
                rec = call_open_meteo_api(city_info)
                logger.info(f"Successfully extracted data for {city_info['name']}: Temp={rec.get('temperature_celsius')}°C")
                return rec
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed for {city_info['name']}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Error extracting weather data for {city_info['name']}: {str(e)}")
                raise
        
        # Extract weather data for all cities
        weather_data_list = [extract_weather_for_city(city) for city in CITIES]
        
        return weather_data_list
    
    # =====================
    # TRANSFORM TASK GROUP
    # =====================
    @task_group(group_id='transform_weather_data')
    def transform_group(weather_data_list: List[Dict[str, Any]]):
        """Task group for transforming weather data"""
        
        @task
        def transform_temperature(weather_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
            Convert temperature from Celsius to Fahrenheit
            
            Args:
                weather_data_list: List of weather data dictionaries
            
            Returns:
                List of weather data with Fahrenheit temperatures added
            """
            logger.info("Transforming temperatures from Celsius to Fahrenheit")
            
            transformed_data = []
            
            for weather in weather_data_list:
                try:
                    temp_celsius = weather.get('temperature_celsius')
                    weather['temperature_fahrenheit'] = to_fahrenheit(temp_celsius)
                    
                    transformed_data.append(weather)
                    
                    logger.info(f"{weather['city']}: {temp_celsius}°C = "
                              f"{weather.get('temperature_fahrenheit')}°F")
                    
                except Exception as e:
                    logger.error(f"Error transforming temperature for {weather.get('city', 'Unknown')}: {str(e)}")
                    raise
            
            return transformed_data
        
        @task
        def add_timestamp(weather_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
            Add extraction timestamp and format existing timestamp
            
            Args:
                weather_data_list: List of weather data dictionaries
            
            Returns:
                List of weather data with timestamps added
            """
            logger.info("Adding timestamps to weather data")
            
            extraction_time = datetime.now(timezone.utc)
            
            for weather in weather_data_list:
                try:
                    # Use helper to normalize timestamp and add extraction date
                    add_extraction_timestamp(weather, extraction_time)
                    
                    logger.info(f"Timestamp added for {weather['city']}: {weather['timestamp']}")
                    
                except Exception as e:
                    logger.error(f"Error adding timestamp for {weather.get('city', 'Unknown')}: {str(e)}")
                    raise
            
            return weather_data_list
        
        @task
        def calculate_statistics(weather_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
            """
            Calculate daily statistics from weather data
            
            Args:
                weather_data_list: List of weather data dictionaries
            
            Returns:
                Dictionary containing daily statistics
            """
            logger.info("Calculating daily weather statistics")
            
            if not weather_data_list:
                logger.warning("No weather data available for statistics calculation")
                return {}
            
            try:
                # Delegate to helper function
                stats = calc_daily_stats(weather_data_list)
                
                logger.info(f"Daily statistics calculated: Avg Temp = {stats['avg_temp_celsius']}°C / "
                          f"{stats['avg_temp_fahrenheit']}°F")
                
                return stats
                
            except Exception as e:
                logger.error(f"Error calculating statistics: {str(e)}")
                raise
        
        # Execute transformation tasks in sequence
        transformed_temps = transform_temperature(weather_data_list)
        timestamped_data = add_timestamp(transformed_temps)
        daily_stats = calculate_statistics(timestamped_data)
        
        return {'weather_data': timestamped_data, 'daily_stats': daily_stats}
    
    # =====================
    # LOAD TASK GROUP
    # =====================
    @task_group(group_id='load_weather_data')
    def load_group(transformed_data: Dict[str, Any]):
        """Task group for loading data into PostgreSQL"""
        
        @task
        def load_weather_records(weather_data_list: List[Dict[str, Any]]) -> int:
            """
            Load weather records into PostgreSQL database
            
            Args:
                weather_data_list: List of weather data dictionaries
            
            Returns:
                Number of records inserted
            """
            logger.info("Loading weather records into PostgreSQL")
            pg_hook = PostgresHook(postgres_conn_id='postgres_default')
            return load_weather_records_to_db(weather_data_list, pg_hook)
        
        @task
        def load_daily_statistics(daily_stats: Dict[str, Any]) -> int:
            """
            Load daily statistics into PostgreSQL database
            
            Args:
                daily_stats: Dictionary containing daily statistics
            
            Returns:
                Number of statistics records inserted
            """
            logger.info("Loading daily statistics into PostgreSQL")
            pg_hook = PostgresHook(postgres_conn_id='postgres_default')
            return load_daily_stats_to_db(daily_stats, pg_hook)
        
        # Load weather records and statistics
        records_count = load_weather_records(transformed_data['weather_data'])
        stats_count = load_daily_statistics(transformed_data['daily_stats'])
        
        return {'records': records_count, 'stats': stats_count}
    
    # =====================
    # DATA QUALITY CHECK
    # =====================
    @task
    def validate_data_quality(load_results: Dict[str, int]) -> bool:
        """
        Perform data quality checks on loaded data
        
        Args:
            load_results: Dictionary containing load results
        
        Returns:
            Boolean indicating if data quality checks passed
        """
        logger.info("Performing data quality checks")
        
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        passed, messages = validate_loaded_data(pg_hook)
        if passed:
            logger.info("🎉 All data quality checks passed!")
        else:
            logger.error("[FAIL] Some data quality checks failed: %s", messages)
        return passed
    
    # =====================
    # NOTIFICATION
    # =====================
    @task
    def send_completion_notification(validation_result: bool, load_results: Dict[str, int]):
        """
        Send notification about pipeline completion
        
        Args:
            validation_result: Boolean indicating if validation passed
            load_results: Dictionary containing load results
        """
        logger.info("=" * 80)
        logger.info("WEATHER ETL PIPELINE COMPLETION NOTIFICATION")
        logger.info("=" * 80)
        
        status = "[SUCCESS]" if validation_result else "[WARNING] COMPLETED WITH WARNINGS"
        
        notification_message = f"""
        Pipeline Status: {status}
        Execution Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}
        
        Summary:
        --------
        • Weather Records Loaded: {load_results['records']}
        • Daily Statistics Loaded: {load_results['stats']}
        • Data Quality Validation: {'PASSED [OK]' if validation_result else 'FAILED [FAIL]'}
        
        Cities Processed:
        -----------------
        {chr(10).join([f"  • {city['name']}" for city in CITIES])}
        
        Database: weather_data
        Table: weather_records, daily_weather_stats
        
        Next Steps:
        -----------
        • Review data quality results in Airflow logs
        • Query weather_records table for detailed data
        • Check daily_weather_stats for aggregated metrics
        
        Pipeline executed successfully!
        """
        
        print(notification_message)
        logger.info(notification_message)
        
        # In production, you would send this via:
        # - Email (using EmailOperator)
        # - Slack (using SlackWebhookOperator)
        # - SMS (using custom operator)
        # - Dashboard/Monitoring system
        
        logger.info("=" * 80)
    
    # =====================
    # DAG EXECUTION FLOW
    # =====================
    
    # Step 1: Extract weather data
    extracted_data = extract_group()
    
    # Step 2: Transform the data
    transformed_data = transform_group(extracted_data)
    
    # Step 3: Load data into database
    load_results = load_group(transformed_data)
    
    # Step 4: Validate data quality
    validation_result = validate_data_quality(load_results)
    
    # Step 5: Send notification
    send_completion_notification(validation_result, load_results)


# Instantiate the DAG
weather_etl_dag = weather_etl_pipeline()