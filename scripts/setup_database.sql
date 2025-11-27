-- Complete Database Setup Script
-- Run this script to set up the entire database from scratch

-- Create database (run as postgres superuser)
-- Note: You may need to run this separately if you don't have superuser access
-- CREATE DATABASE weather_data;

-- Connect to the database
\c weather_data;

-- Create user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'weather_user') THEN
      CREATE USER weather_user WITH PASSWORD 'weather_pass';
   END IF;
END
$do$;

-- Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE weather_data TO weather_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO weather_user;

-- Create tables
\i ../sql/create_tables.sql

-- Grant table privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weather_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO weather_user;

-- Create indexes
\i ../sql/create_indexes.sql

-- Create views
\i ../sql/views.sql

-- Verify setup
\dt
\di
\dv

-- Display summary
SELECT 'Database setup completed successfully!' as status;
SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
SELECT COUNT(*) as view_count FROM information_schema.views WHERE table_schema = 'public';
SELECT COUNT(*) as index_count FROM pg_indexes WHERE schemaname = 'public';

