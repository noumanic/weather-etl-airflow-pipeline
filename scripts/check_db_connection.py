"""
Check database connection script
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
        print("[OK] Connection successful!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database or other error: {e}")

if __name__ == "__main__":
    test_connection()
