# Weather ETL Pipeline - Setup Guide

Complete guide for setting up and running the Weather ETL Pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Pipeline](#running-the-pipeline)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Windows 10/11 with WSL2, macOS, or Linux
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: At least 10GB free
- **Network**: Internet connection for API calls

### Software Requirements

- **Docker Desktop**: Version 20.10 or higher
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Ensure WSL2 backend is enabled (Windows)

- **Git**: For cloning the repository
  - [Download Git](https://git-scm.com/downloads)

- **Python**: Version 3.8+ (for local development/testing)
  - [Download Python](https://www.python.org/downloads/)

## Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd weather-etl-pipeline
```

### Step 2: Create Environment File

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit the file with your preferences
# nano .env  # or use your preferred editor
```

Example `.env` contents:

```env
# Airflow Configuration
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow

# PostgreSQL Configuration
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
POSTGRES_PORT=5432

# Weather Database
WEATHER_DB_NAME=weather_data
WEATHER_DB_USER=weather_user
WEATHER_DB_PASSWORD=weather_pass
```

### Step 3: Build and Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

Expected output:
```
NAME                        STATUS
airflow-webserver           Up (healthy)
airflow-scheduler           Up (healthy)
postgres                    Up (healthy)
```

### Step 4: Wait for Services to Initialize

The services may take 2-3 minutes to fully initialize. Monitor the logs:

```bash
# Watch Airflow webserver logs
docker-compose logs -f airflow-webserver

# Watch Airflow scheduler logs
docker-compose logs -f airflow-scheduler
```

## Configuration

### Airflow Connection Setup

1. **Access Airflow UI**
   - URL: http://localhost:8080
   - Username: `airflow` (or value from `.env`)
   - Password: `airflow` (or value from `.env`)

2. **Configure PostgreSQL Connection**
   - Navigate to: **Admin → Connections**
   - Click the **+** button to add a new connection
   - Fill in the details:
     ```
     Connection Id: postgres_default
     Connection Type: Postgres
     Host: postgres
     Schema: weather_data
     Login: weather_user
     Password: weather_pass
     Port: 5432
     ```
   - Click **Save**

3. **Verify Connection**
   - Click the **Test** button
   - Should see: "Connection successfully tested"

### Cities Configuration

Edit `config/cities.py` to add or modify cities:

```python
CITIES = [
    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    # Add more cities...
]
```

### Schedule Configuration

Edit `dags/weather_etl_dag.py` to change the schedule:

```python
@dag(
    dag_id='weather_etl_pipeline',
    schedule_interval='@daily',  # Change to @hourly, cron expression, etc.
    # ...
)
```

## Running the Pipeline

### Option 1: Manual Trigger (Recommended for First Run)

1. Go to Airflow UI: http://localhost:8080
2. Find `weather_etl_pipeline` in the DAGs list
3. Toggle the DAG to **ON** (if not already)
4. Click the **Play** button (▶️) to trigger manually
5. Click on the DAG name to see the execution graph

### Option 2: Command Line Trigger

```bash
# Trigger the DAG
docker exec -it <airflow-scheduler-container> \
    airflow dags trigger weather_etl_pipeline

# List all DAGs
docker exec -it <airflow-scheduler-container> \
    airflow dags list

# Test a specific task
docker exec -it <airflow-scheduler-container> \
    airflow tasks test weather_etl_pipeline <task_id> 2024-01-01
```

### Option 3: Scheduled Execution

Once enabled, the DAG will run automatically based on the schedule:
- Default: `@daily` (midnight every day)
- Can be changed to `@hourly`, `@weekly`, or custom cron expression

## Verification

### 1. Check DAG Execution

**In Airflow UI:**
- Go to the DAG's **Graph View**
- Verify all tasks are green (successful)
- Check task logs for any warnings or errors

**Expected Task Flow:**
```
extract_weather_data → transform_weather_data → load_weather_data → validate_data_quality → send_completion_notification
```

### 2. Verify Database Records

**Connect to PostgreSQL:**

```bash
# Connect to database
docker exec -it <postgres-container> \
    psql -U weather_user -d weather_data

# Check record count
SELECT COUNT(*) FROM weather_records;

# View recent records
SELECT city, temperature_celsius, timestamp
FROM weather_records
ORDER BY extraction_date DESC
LIMIT 10;

# Check statistics
SELECT * FROM daily_weather_stats
ORDER BY date DESC;

# Exit
\q
```

### 3. Test API Connection

```bash
# Run component test script
python scripts/test_components.py
```

Expected output:
```
[PASS] API Connection: PASSED
[PASS] Temperature Conversion: PASSED
[PASS] Daily Statistics: PASSED
[PASS] Timestamp Functions: PASSED
[PASS] Weather Descriptions: PASSED
```

### 4. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 airflow-scheduler
```

## Troubleshooting

### Issue: Airflow webserver not accessible

**Solution:**
```bash
# Check container status
docker-compose ps

# Restart webserver
docker-compose restart airflow-webserver

# Check logs
docker-compose logs airflow-webserver
```

### Issue: DAG not appearing in UI

**Solution:**
```bash
# Check for syntax errors
docker exec -it <airflow-scheduler> \
    python /opt/airflow/dags/weather_etl_dag.py

# Restart scheduler
docker-compose restart airflow-scheduler

# Force DAG refresh
docker exec -it <airflow-scheduler> \
    airflow dags list-import-errors
```

### Issue: Database connection failed

**Solution:**
```bash
# Verify database is running
docker exec -it <postgres-container> \
    psql -U weather_user -d weather_data -c "SELECT 1"

# Check connection in Airflow
# Go to Admin → Connections → postgres_default → Test

# Recreate connection
docker exec -it <airflow-scheduler> \
    airflow connections delete postgres_default

docker exec -it <airflow-scheduler> \
    airflow connections add postgres_default \
    --conn-type postgres \
    --conn-host postgres \
    --conn-port 5432 \
    --conn-login weather_user \
    --conn-password weather_pass \
    --conn-schema weather_data
```

### Issue: API requests failing

**Solution:**
```bash
# Test API manually
curl "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m"

# Check task logs in Airflow UI
# Look for retry attempts and error messages

# Verify internet connectivity
docker exec -it <airflow-scheduler> ping -c 3 api.open-meteo.com
```

### Issue: Disk space running low

**Solution:**
```bash
# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete

# Clean up old data
python scripts/cleanup_old_data.py --retention-days 90 --execute

# Remove unused Docker images
docker system prune -a
```

### Issue: Tasks failing with "Import Error"

**Solution:**
```bash
# Check Python path
docker exec -it <airflow-scheduler> \
    python -c "import sys; print('\n'.join(sys.path))"

# Verify helper module exists
docker exec -it <airflow-scheduler> \
    ls -la /opt/airflow/dags/helpers.py

# Restart scheduler
docker-compose restart airflow-scheduler
```

## Next Steps

1. **Monitor the Pipeline**
   - Use Airflow UI to track daily runs
   - Set up email notifications (optional)
   - Review data quality metrics

2. **Customize Configuration**
   - Add more cities to track
   - Adjust schedule frequency
   - Modify data retention policies

3. **Explore the Data**
   - Use the Jupyter notebooks in `notebooks/`
   - Run sample SQL queries from `sql/sample_queries.sql`
   - Create custom analytics views

4. **Set Up Alerts** (Optional)
   - Configure email on failure
   - Set up Slack notifications
   - Integrate with monitoring tools

## Additional Resources

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [TaskFlow API Guide](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
- [Open-Meteo API Docs](https://open-meteo.com/en/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

If you encounter issues not covered in this guide:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review [Architecture Documentation](architecture.md)
3. Examine Airflow task logs for detailed error messages
4. Consult the project's issue tracker