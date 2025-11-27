"""
Test database connection script
Run this to verify PostgreSQL connection is working
"""

def test_connection():
    """Test PostgreSQL connection and query weather data"""
    import psycopg2
    from psycopg2 import sql
    try:
        # Connection parameters
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'weather_data',
            'user': 'weather_user',
            'password': 'weather_pass'
        }
        
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("[OK] Connection successful!\n")
        
        # Test query 1: Count weather records
        print("=" * 60)
        print("TEST 1: Count Weather Records")
        print("=" * 60)
        cursor.execute("SELECT COUNT(*) FROM weather_records;")
        count = cursor.fetchone()[0]
        print(f"Total weather records: {count}\n")
        
        # Test query 2: Get latest records
        if count > 0:
            print("=" * 60)
            print("TEST 2: Latest Weather Records")
            print("=" * 60)
            cursor.execute("""
                SELECT city, temperature_celsius, temperature_fahrenheit, 
                       humidity, wind_speed, timestamp
                FROM weather_records
                ORDER BY extraction_date DESC
                LIMIT 5;
            """)
            
            records = cursor.fetchall()
            print(f"{'City':<15} {'Temp(°C)':<10} {'Temp(°F)':<10} {'Humidity':<10} {'Wind Speed':<12} {'Timestamp'}")
            print("-" * 85)
            for record in records:
                city, temp_c, temp_f, humidity, wind, timestamp = record
                print(f"{city:<15} {temp_c:<10.1f} {temp_f:<10.1f} {humidity:<10.1f} {wind:<12.1f} {timestamp}")
        
        # Test query 3: Daily statistics
        print("\n" + "=" * 60)
        print("TEST 3: Daily Statistics")
        print("=" * 60)
        cursor.execute("SELECT COUNT(*) FROM daily_weather_stats;")
        stats_count = cursor.fetchone()[0]
        print(f"Total daily statistics records: {stats_count}\n")
        
        if stats_count > 0:
            cursor.execute("""
                SELECT city, date, avg_temp_celsius, avg_temp_fahrenheit,
                       max_temp_celsius, min_temp_celsius
                FROM daily_weather_stats
                ORDER BY date DESC
                LIMIT 5;
            """)
            
            stats = cursor.fetchall()
            print(f"{'City':<15} {'Date':<12} {'Avg(°C)':<10} {'Avg(°F)':<10} {'Max(°C)':<10} {'Min(°C)'}")
            print("-" * 75)
            for stat in stats:
                city, date, avg_c, avg_f, max_c, min_c = stat
                print(f"{city:<15} {date} {avg_c:<10.1f} {avg_f:<10.1f} {max_c:<10.1f} {min_c:<10.1f}")
        
        print("\n" + "=" * 60)
        print("[OK] All tests completed successfully!")
        print("=" * 60)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database or other error: {e}")


if __name__ == "__main__":
    test_connection()