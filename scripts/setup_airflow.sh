#!/bin/bash

# Weather ETL Pipeline - Airflow Setup Script
# Automates Airflow initialization and configuration

set -e  # Exit on error

echo "========================================="
echo "Weather ETL Pipeline - Airflow Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AIRFLOW_HOME="${AIRFLOW_HOME:-./}"
AIRFLOW_VERSION="2.8.0"
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"

echo "Configuration:"
echo "  Airflow Home: $AIRFLOW_HOME"
echo "  Airflow Version: $AIRFLOW_VERSION"
echo "  Python Version: $PYTHON_VERSION"
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo -e "${GREEN}[OK]${NC} Running in Docker container"
    IN_DOCKER=true
else
    echo -e "${YELLOW}⚠${NC} Running outside Docker"
    IN_DOCKER=false
fi
echo ""

# Function to check if service is ready
wait_for_service() {
    local service=$1
    local host=$2
    local port=$3
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo -e "${GREEN}[OK]${NC} $service is ready"
            return 0
        fi
        
        echo "  Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}[FAIL]${NC} $service failed to start"
    return 1
}

# Check PostgreSQL connection
echo "========================================="
echo "Checking Database Connection"
echo "========================================="

if [ "$IN_DOCKER" = true ]; then
    POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
else
    POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
fi

POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-airflow}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-airflow}"
POSTGRES_DB="${POSTGRES_DB:-airflow}"

# Wait for PostgreSQL
wait_for_service "PostgreSQL" "$POSTGRES_HOST" "$POSTGRES_PORT"

# Test database connection
echo "Testing database connection..."
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Database connection successful"
else
    echo -e "${RED}[FAIL]${NC} Database connection failed"
    echo "Please check database credentials and ensure PostgreSQL is running"
    exit 1
fi
echo ""

# Initialize Airflow database
echo "========================================="
echo "Initializing Airflow Database"
echo "========================================="

if [ "$IN_DOCKER" = true ]; then
    echo "Airflow database initialization handled by Docker entrypoint"
else
    echo "Running: airflow db init"
    airflow db init || {
        echo -e "${RED}[FAIL]${NC} Failed to initialize Airflow database"
        exit 1
    }
    echo -e "${GREEN}[OK]${NC} Airflow database initialized"
fi
echo ""

# Create Airflow admin user
echo "========================================="
echo "Creating Airflow Admin User"
echo "========================================="

AIRFLOW_USERNAME="${_AIRFLOW_WWW_USER_USERNAME:-airflow}"
AIRFLOW_PASSWORD="${_AIRFLOW_WWW_USER_PASSWORD:-airflow}"
AIRFLOW_EMAIL="${AIRFLOW_EMAIL:-admin@example.com}"

if [ "$IN_DOCKER" = true ]; then
    echo "Admin user creation handled by Docker entrypoint"
else
    # Check if user already exists
    if airflow users list 2>/dev/null | grep -q "$AIRFLOW_USERNAME"; then
        echo -e "${YELLOW}⚠${NC} User '$AIRFLOW_USERNAME' already exists"
    else
        echo "Creating admin user: $AIRFLOW_USERNAME"
        airflow users create \
            --username "$AIRFLOW_USERNAME" \
            --firstname Admin \
            --lastname User \
            --role Admin \
            --email "$AIRFLOW_EMAIL" \
            --password "$AIRFLOW_PASSWORD" || {
                echo -e "${RED}[FAIL]${NC} Failed to create admin user"
                exit 1
            }
        echo -e "${GREEN}[OK]${NC} Admin user created"
    fi
fi
echo ""

# Configure Airflow connections
echo "========================================="
echo "Configuring Airflow Connections"
echo "========================================="

# PostgreSQL connection for weather data
WEATHER_DB_HOST="${POSTGRES_HOST}"
WEATHER_DB_PORT="${POSTGRES_PORT}"
WEATHER_DB_NAME="weather_data"
WEATHER_DB_USER="weather_user"
WEATHER_DB_PASSWORD="weather_pass"

echo "Configuring postgres_default connection..."
airflow connections delete postgres_default 2>/dev/null || true
airflow connections add postgres_default \
    --conn-type postgres \
    --conn-host "$WEATHER_DB_HOST" \
    --conn-port "$WEATHER_DB_PORT" \
    --conn-login "$WEATHER_DB_USER" \
    --conn-password "$WEATHER_DB_PASSWORD" \
    --conn-schema "$WEATHER_DB_NAME" && {
        echo -e "${GREEN}[OK]${NC} postgres_default connection configured"
    } || {
        echo -e "${YELLOW}⚠${NC} Failed to configure connection (may already exist)"
    }
echo ""

# Verify DAG files
echo "========================================="
echo "Verifying DAG Files"
echo "========================================="

DAG_FOLDER="${AIRFLOW_HOME}/dags"

if [ -d "$DAG_FOLDER" ]; then
    echo "DAG folder: $DAG_FOLDER"
    
    DAG_COUNT=$(find "$DAG_FOLDER" -name "*.py" ! -name "__*" | wc -l)
    echo "DAG files found: $DAG_COUNT"
    
    if [ "$DAG_COUNT" -gt 0 ]; then
        echo ""
        echo "DAG files:"
        find "$DAG_FOLDER" -name "*.py" ! -name "__*" -exec basename {} \;
        echo -e "${GREEN}[OK]${NC} DAG files verified"
    else
        echo -e "${YELLOW}⚠${NC} No DAG files found"
    fi
else
    echo -e "${RED}[FAIL]${NC} DAG folder not found: $DAG_FOLDER"
fi
echo ""

# Test DAG parsing
echo "========================================="
echo "Testing DAG Parsing"
echo "========================================="

if [ -f "$DAG_FOLDER/weather_etl_dag.py" ]; then
    echo "Testing weather_etl_dag.py..."
    python "$DAG_FOLDER/weather_etl_dag.py" && {
        echo -e "${GREEN}[OK]${NC} DAG parsed successfully"
    } || {
        echo -e "${RED}[FAIL]${NC} DAG parsing failed"
        echo "Please check the DAG file for syntax errors"
    }
else
    echo -e "${YELLOW}⚠${NC} weather_etl_dag.py not found"
fi
echo ""

# Display setup summary
echo "========================================="
echo "Setup Summary"
echo "========================================="
echo -e "${GREEN}[OK]${NC} Airflow setup completed successfully!"
echo ""
echo "Access Information:"
echo "  Airflow Web UI: http://localhost:8080"
echo "  Username: $AIRFLOW_USERNAME"
echo "  Password: $AIRFLOW_PASSWORD"
echo ""
echo "Database Connection:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo ""
echo "Next Steps:"
echo "  1. Access Airflow UI at http://localhost:8080"
echo "  2. Enable the 'weather_etl_pipeline' DAG"
echo "  3. Trigger a test run"
echo "  4. Monitor execution in the UI"
echo ""
echo "========================================="
echo ""
