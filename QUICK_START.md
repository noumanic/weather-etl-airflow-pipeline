# Weather ETL Pipeline - Quick Start Guide

Get the Weather ETL Pipeline up and running in 10 minutes!

## Prerequisites

Before starting, ensure you have:
- Docker Desktop installed and running
- At least 8GB RAM available
- 10GB free disk space
- Internet connection

## Quick Installation

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd weather-etl-pipeline
```

### Step 2: Create Environment File

Create a `.env` file in the project root:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

The default values in `.env.example` are ready to use. You can customize them if needed.

### Step 3: Start the Services

```bash
docker-compose up -d
```

This will:
- Pull necessary Docker images (first time only - may take 5-10 minutes)
- Start PostgreSQL database
- Initialize Airflow
- Create default admin user
- Set up the weather database

### Step 4: Wait for Initialization

**Wait for services to be healthy** (usually 2-3 minutes):

```bash
# Check service status
docker-compose ps

# Watch logs (optional)
docker-compose logs -f airflow-webserver
```

Expected output:
```
NAME                          STATUS
postgres                      Up (healthy)
airflow-webserver             Up (healthy)
airflow-scheduler             Up (healthy)
```

## First Run

### Step 1: Access Airflow UI

1. Open your browser and go to: **http://localhost:8080**

2. Login with default credentials:
   - **Username**: `airflow`
   - **Password**: `airflow`

### Step 2: Configure Database Connection

1. In Airflow UI, navigate to: **Admin → Connections**

2. Click the **+** button (Add a new record)

3. Fill in the connection details:
   ```
   Connection Id:    postgres_default
   Connection Type:  Postgres
   Host:            postgres
   Schema:          weather_data
   Login:           weather_user
   Password:        weather_pass
   Port:            5432
   ```

4. Click **Test** to verify the connection

5. Click **Save**

### Step 3: Enable and Trigger the DAG

1. Go back to the **DAGs** page (Home)

2. Find `weather_etl_pipeline` in the list

3. Toggle the switch to **ON** (it should turn blue/green)

4. Click the **▶️ Play button** (Trigger DAG) to start a manual run

5. Click on the DAG name to see the execution progress

### Step 4: Monitor Execution

The DAG will execute through these stages:

```
Extract (API calls)
    ↓
Transform (Temperature conversion, timestamps, statistics)
    ↓
Load (Insert to database)
    ↓
Validate (Data quality checks)
    ↓
Notify (Completion notification)
```

**Expected duration**: 30-60 seconds

All task boxes should turn **green** ✅ when successful.

## Verify Success

### Check the Data

**Option 1: Using SQL**

```bash
# Connect to the database
docker exec -it weather-etl-pipeline-neuralnouman-postgres-1 psql -U weather_user -d weather_data

# View recent weather records
SELECT city, temperature_celsius, temperature_fahrenheit, humidity, weather_condition, timestamp
FROM weather_records
ORDER BY extraction_date DESC
LIMIT 10;

# View daily statistics
SELECT * FROM daily_weather_stats ORDER BY date DESC;

# Exit
\q
```

**Option 2: View in Airflow Logs**

1. Click on any green task in the Graph View
2. Click **Log** button
3. Scroll through the logs to see execution details

Expected log entries:
```
[OK] Successfully extracted data for New York: Temp=15.5°C
[OK] New York: 15.5°C = 59.9°F
[OK] Successfully loaded 10 weather records
[OK] All data quality checks passed!
```

### Check the Notification

Look for the completion notification in the **send_completion_notification** task log:

```
========================================================
WEATHER ETL PIPELINE COMPLETION NOTIFICATION
========================================================
Pipeline Status: [SUCCESS]
Execution Date: 2024-01-15 12:00:00 UTC

Summary:
--------
• Weather Records Loaded: 10
• Daily Statistics Loaded: 10
• Data Quality Validation: PASSED [OK]

Cities Processed:
-----------------
  • New York
  • London
  • Tokyo
  • Paris
  • Sydney
  • Dubai
  • Singapore
  • Mumbai
  • Toronto
  • Berlin
```

## Test the Components

Run the component test script:

```bash
# Install dependencies locally (if not already installed)
pip install requests psycopg2-binary

# Run tests
python scripts/test_components.py
```

Expected output:
```
[PASS] API Connection: PASSED
[PASS] Temperature Conversion: PASSED
[PASS] Daily Statistics: PASSED
[PASS] Timestamp Functions: PASSED
[PASS] Weather Descriptions: PASSED

Total: 5/5 tests passed
```

## Explore the Data

### Option 1: SQL Queries

Check out the sample queries in `sql/sample_queries.sql`:

```bash
docker exec -it weather-etl-pipeline-postgres-1 psql -U weather_user -d weather_data -f /opt/airflow/sql/sample_queries.sql
```

### Option 2: Jupyter Notebooks

```bash
# Install Jupyter (if not already installed)
pip install jupyter pandas matplotlib seaborn psycopg2-binary

# Start Jupyter
jupyter notebook

# Open notebooks/data_exploration.ipynb
```

### Option 3: Analytical Views

```sql
-- Current weather for all cities
SELECT * FROM v_current_weather;

-- Daily summary
SELECT * FROM v_daily_weather_summary
WHERE date >= CURRENT_DATE - INTERVAL '7 days';

-- Temperature extremes
SELECT * FROM v_temperature_extremes;

-- Data quality dashboard
SELECT * FROM v_data_quality_dashboard
ORDER BY date DESC;
```

## Customize the Pipeline

### Add More Cities

Edit `config/cities.py`:

```python
CITIES = [
    {"name": "Your City", "latitude": XX.XXXX, "longitude": YY.YYYY},
    # Add more cities...
]
```

Then restart the scheduler:
```bash
docker-compose restart airflow-scheduler
```

### Change Schedule

Edit `dags/weather_etl_dag.py`:

```python
@dag(
    dag_id='weather_etl_pipeline',
    schedule_interval='@hourly',  # Change from @daily to @hourly
    # ...
)
```

### Configure Notifications

Edit `.env` file to add email/Slack settings:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_MAIL_FROM=your-email@gmail.com

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Troubleshooting

### Issue: Cannot access Airflow UI

**Solution:**
```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs airflow-webserver

# Restart if needed
docker-compose restart airflow-webserver
```

### Issue: DAG not appearing

**Solution:**
```bash
# Check for errors
docker-compose logs airflow-scheduler

# Verify DAG file
docker exec -it weather-etl-pipeline-neuralnouman-airflow-scheduler-1 python /opt/airflow/dags/weather_etl_dag.py

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Issue: Database connection failed

**Solution:**
1. Verify connection details in Airflow UI (Admin → Connections)
2. Ensure connection ID is exactly `postgres_default`
3. Host should be `postgres` (not localhost)
4. Test the connection using the Test button

### Issue: Tasks failing

**Solution:**
1. Click on the failed task (red box)
2. Click **Log** to see error details
3. Check common issues:
   - Network connectivity for API calls
   - Database permissions
   - Data validation failures

For more help, see [docs/troubleshooting.md](docs/troubleshooting.md)

## Cleanup

### Stop the Services

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Remove Everything

```bash
# Remove containers, volumes, and images
docker-compose down -v --rmi all

# Clean up Docker system
docker system prune -a
```

## Next Steps

Now that your pipeline is running:

1. **Explore the Documentation**
   - [Setup Guide](docs/setup_guide.md) - Detailed setup instructions
   - [Architecture](docs/architecture.md) - System design and components
   - [API Documentation](docs/api_documentation.md) - Open-Meteo API details
   - [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

2. **Customize the Pipeline**
   - Add more cities to track
   - Change the schedule frequency
   - Add email or Slack notifications
   - Create custom analytics queries

3. **Analyze the Data**
   - Use Jupyter notebooks for analysis
   - Create custom SQL queries
   - Build dashboards with your favorite BI tool

4. **Run Tests**
   ```bash
   # Run unit tests
   pytest tests/ -v
   
   # Run integration tests
   pytest tests/test_integration.py -v
   ```

5. **Set Up Monitoring**
   - Review DAG runs daily
   - Check data quality metrics
   - Monitor disk space and performance

## Success!

Congratulations! Your Weather ETL Pipeline is now running and collecting weather data.

**What's happening now:**
- Every day at midnight, the pipeline will automatically run
- It fetches weather data for 10 cities
- Data is transformed and stored in PostgreSQL
- Quality checks ensure data integrity
- Notifications confirm successful completion

**Access your data:**
- Database: localhost:5432
- Airflow UI: http://localhost:8080
- Logs: `./logs/` directory

## Tips

- **Monitor regularly**: Check the Airflow UI daily to ensure runs are successful
- **Review logs**: Task logs provide detailed execution information
- **Back up data**: Run regular database backups (see `scripts/` for automation)
- **Clean old data**: Use `scripts/cleanup_old_data.py` to manage retention
- **Optimize queries**: Add indexes for frequently used queries

## Support

If you encounter any issues:
1. Check the [Troubleshooting Guide](docs/troubleshooting.md)
2. Review task logs in Airflow UI
3. Check Docker container logs
4. Verify database connectivity

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f airflow-scheduler

# Check container status
docker-compose ps

# Restart a service
docker-compose restart [service-name]

# Access PostgreSQL
docker exec -it weather-etl-pipeline-neuralnouman-postgres-1 psql -U weather_user -d weather_data

# Run component tests
python scripts/test_components.py

# Run unit tests
pytest tests/ -v

# Clean up old data
python scripts/cleanup_old_data.py --retention-days 90 --execute
```

Happy data engineering!

