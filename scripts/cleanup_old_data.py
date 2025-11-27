#!/usr/bin/env python3
"""
Data Cleanup Script
Removes old weather data based on retention policy
"""

import psycopg2
import argparse
from datetime import datetime, timedelta
import sys


def cleanup_old_data(
    host='localhost',
    port=5432,
    database='weather_data',
    user='weather_user',
    password='weather_pass',
    retention_days=90,
    dry_run=True
):
    """
    Clean up old weather data
    
    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
        retention_days: Number of days to retain data
        dry_run: If True, only show what would be deleted
    """
    
    try:
        # Connect to database
        print(f"\nConnecting to database {database}@{host}:{port}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        print(f"\nRetention Policy: {retention_days} days")
        print(f"Cutoff Date: {cutoff_date.date()}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        
        # Check weather_records
        print("\n" + "="*60)
        print("Weather Records")
        print("="*60)
        
        cursor.execute("""
            SELECT COUNT(*) FROM weather_records
            WHERE extraction_date < %s
        """, (cutoff_date,))
        
        records_to_delete = cursor.fetchone()[0]
        print(f"Records to delete: {records_to_delete}")
        
        if not dry_run and records_to_delete > 0:
            cursor.execute("""
                DELETE FROM weather_records
                WHERE extraction_date < %s
            """, (cutoff_date,))
            print(f"[OK] Deleted {records_to_delete} old weather records")
        
        # Check daily_weather_stats
        print("\n" + "="*60)
        print("Daily Weather Statistics")
        print("="*60)
        
        cursor.execute("""
            SELECT COUNT(*) FROM daily_weather_stats
            WHERE date < %s
        """, (cutoff_date.date(),))
        
        stats_to_delete = cursor.fetchone()[0]
        print(f"Statistics records to delete: {stats_to_delete}")
        
        if not dry_run and stats_to_delete > 0:
            cursor.execute("""
                DELETE FROM daily_weather_stats
                WHERE date < %s
            """, (cutoff_date.date(),))
            print(f"[OK] Deleted {stats_to_delete} old statistics records")
        
        # Check etl_audit_log
        print("\n" + "="*60)
        print("ETL Audit Log")
        print("="*60)
        
        cursor.execute("""
            SELECT COUNT(*) FROM etl_audit_log
            WHERE run_date < %s
        """, (cutoff_date,))
        
        audit_to_delete = cursor.fetchone()[0]
        print(f"Audit log entries to delete: {audit_to_delete}")
        
        if not dry_run and audit_to_delete > 0:
            cursor.execute("""
                DELETE FROM etl_audit_log
                WHERE run_date < %s
            """, (cutoff_date,))
            print(f"[OK] Deleted {audit_to_delete} old audit log entries")
        
        # Commit changes
        if not dry_run:
            conn.commit()
            print("\n[OK] All changes committed")
            
            # Vacuum tables to reclaim space
            print("\nVacuuming tables to reclaim space...")
            conn.set_isolation_level(0)  # Autocommit mode for VACUUM
            cursor.execute("VACUUM ANALYZE weather_records")
            cursor.execute("VACUUM ANALYZE daily_weather_stats")
            cursor.execute("VACUUM ANALYZE etl_audit_log")
            print("[OK] Vacuum completed")
        else:
            print("\n⚠️  DRY RUN - No changes made")
            print("   Run with --execute flag to perform cleanup")
        
        # Summary
        total_to_delete = records_to_delete + stats_to_delete + audit_to_delete
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Total records to delete: {total_to_delete}")
        print(f"  - Weather records: {records_to_delete}")
        print(f"  - Statistics records: {stats_to_delete}")
        print(f"  - Audit log entries: {audit_to_delete}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Clean up old weather data based on retention policy'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Database host (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5432,
        help='Database port (default: 5432)'
    )
    
    parser.add_argument(
        '--database',
        default='weather_data',
        help='Database name (default: weather_data)'
    )
    
    parser.add_argument(
        '--user',
        default='weather_user',
        help='Database user (default: weather_user)'
    )
    
    parser.add_argument(
        '--password',
        default='weather_pass',
        help='Database password (default: weather_pass)'
    )
    
    parser.add_argument(
        '--retention-days',
        type=int,
        default=90,
        help='Number of days to retain data (default: 90)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute cleanup (default: dry run)'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Weather Data Cleanup Script")
    print("="*60)
    print(f"Run Time: {datetime.now()}")
    
    success = cleanup_old_data(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
        retention_days=args.retention_days,
        dry_run=not args.execute
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
