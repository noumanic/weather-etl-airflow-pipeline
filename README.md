# Weather ETL Pipeline Using Apache Airflow

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.8.0-red.svg)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A production-ready, scalable ETL pipeline for real-time weather data collection, transformation, and storage using Apache Airflow, PostgreSQL, and Docker. Built for MLOps best practices with comprehensive monitoring, testing, and data quality validation.

---

## Pipeline in Action

### Airflow DAG Execution View
![Airflow ETL Runs](airflow_etl_runs.png)
*Successfully executed ETL pipeline showing all task groups and their execution status*

### Pipeline Graph Visualization
![Pipeline Graph](graph_result.png)
*Visual representation of the ETL pipeline flow with task dependencies*

---

## Features

### Core Capabilities
- **Extract**: Fetch real-time weather data from Open-Meteo API for multiple cities worldwide
- **Transform**: Convert temperatures (Celsius → Fahrenheit), add timestamps, calculate daily statistics
- **Load**: Store data in PostgreSQL with proper error handling and data validation
- **Validate**: Comprehensive data quality checks (null values, valid ranges, conversion accuracy)
- **Notify**: Send completion notifications with pipeline summary and metrics

### Advanced Features
- **TaskFlow API**: Modern Airflow 2.8+ implementation with decorators
- **Task Groups**: Organized pipeline structure for better visualization
- **Automatic Retries**: Configurable retry logic with exponential backoff
- **Data Quality Monitoring**: Built-in data quality dashboard view
- **Idempotency**: Safe to re-run without data duplication
- **Docker Compose**: One-command deployment for all services
- **Jupyter Notebooks**: Data exploration and pipeline monitoring notebooks included
- **Comprehensive Testing**: Unit and integration tests for all components

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        External Services                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐                                              │
│  │  Open-Meteo    │  ← Real-time weather data API                │
│  │     API        │                                              │
│  └───────┬────────┘                                              │
│          │                                                       │
└──────────┼───────────────────────────────────────────────────────┘
           │
           │ HTTPS REST API
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Apache Airflow (Orchestration)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                Weather ETL DAG                         │     │
│  │  (TaskFlow API + Task Groups)                          │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │                                                        │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  1. EXTRACT  (Task Group)                        │  │     │
│  │  ├──────────────────────────────────────────────────┤  │     │
│  │  │  • API Calls (parallel for each city)            │  │     │
│  │  │  • Error handling & retries (3 attempts)         │  │     │
│  │  │  • Rate limiting                                 │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  │                        │                               │     │
│  │                        ▼                               │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  2. TRANSFORM (Task Group)                       │  │     │
│  │  ├──────────────────────────────────────────────────┤  │     │
│  │  │  • Convert Celsius → Fahrenheit                  │  │     │
│  │  │  • Add extraction timestamps                     │  │     │
│  │  │  • Calculate daily statistics                    │  │     │
│  │  │  • Data validation                               │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  │                        │                               │     │
│  │                        ▼                               │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  3. LOAD (Task Group)                            │  │     │
│  │  ├──────────────────────────────────────────────────┤  │     │
│  │  │  • Insert weather records                        │  │     │
│  │  │  • Insert daily statistics                       │  │     │
│  │  │  • Transaction management                        │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  │                        │                               │     │
│  │                        ▼                               │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  4. VALIDATE (Task)                              │  │     │
│  │  ├──────────────────────────────────────────────────┤  │     │
│  │  │  • Check data completeness                       │  │     │
│  │  │  • Validate ranges                               │  │     │
│  │  │  • Verify conversions                            │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  │                        │                               │     │
│  │                        ▼                               │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  5. NOTIFY (Task)                                │  │     │
│  │  ├──────────────────────────────────────────────────┤  │     │
│  │  │  • Generate summary report                       │  │     │
│  │  │  • Log completion status                         │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  │                                                        │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌───────────────────┐         ┌────────────────────┐           │
│  │  Airflow          │         │   Airflow          │           │
│  │  Webserver        │◄────────┤   Scheduler        │           │
│  │  (UI/API)         │         │   (DAG Execution)  │           │
│  └───────────────────┘         └────────────────────┘           │
│                                                                 │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
                                    │ SQL Queries
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PostgreSQL Database                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Schema: weather_data                                   │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │                                                         │    │
│  │  Tables:                                                │    │
│  │  • weather_records      (raw data)                      │    │
│  │  • daily_weather_stats  (aggregated)                    │    │
│  │  • etl_audit_log        (pipeline runs)                 │    │
│  │                                                         │    │
│  │  Views:                                                 │    │
│  │  • v_current_weather                                    │    │
│  │  • v_daily_weather_summary                              │    │
│  │  • v_temperature_extremes                               │    │
│  │  • v_data_quality_dashboard                             │    │
│  │  • v_pipeline_performance                               │    │
│  │                                                         │    │
│  │  Indexes:                                               │    │
│  │  • city, timestamp composite                            │    │
│  │  • extraction_date                                      │    │
│  │  • date-based indexes                                   │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Software
- **Docker Desktop** (v20.10+) - [Download](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (v2.0+) - Included with Docker Desktop
- **Git** - For version control
- **Python 3.10+** - For local development and testing (optional)

### System Requirements
- **RAM**: 8GB minimum (16GB recommended for production)
- **Disk Space**: 10GB free space
- **OS**: Windows 10/11 with WSL2, macOS, or Linux
- **Network**: Internet connection for API access

### Optional Tools
- **pgAdmin** or **DBeaver** - For database management
- **Postman** - For API testing
- **Jupyter Notebook** - For data exploration (included in notebooks)

---

## Quick Start Guide

### Step 1: Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/YOUR_USERNAME/etl-pipeline-for-weather-data-using-airflow.git

# Navigate to project directory
cd etl-pipeline-for-weather-data-using-airflow-neuralnouman
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root (optional, uses defaults if not provided):

```bash
# PostgreSQL Configuration
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW__CORE__LOAD_EXAMPLES=false
```

### Step 3: Start All Services

```bash
# Start all Docker containers in detached mode
docker-compose up -d

# Check container status (all should be "healthy")
docker-compose ps

# View real-time logs
docker-compose logs -f
```

**Expected Output:**
```
[OK] postgres                 - healthy
[OK] airflow-webserver        - healthy
[OK] airflow-scheduler        - healthy
[OK] airflow-init            - exited (0)
```

### Step 4: Access Airflow Web UI

1. Open your browser and navigate to: **http://localhost:8080**
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin`

### Step 5: Verify PostgreSQL Connection

The connection is pre-configured via environment variables. To verify:

1. In Airflow UI, go to **Admin** → **Connections**
2. Find `postgres_default` connection
3. Should show:
   - **Host**: `postgres`
   - **Schema**: `weather_data`
   - **Login**: `weather_user`
   - **Port**: `5432`

### Step 6: Trigger the Weather ETL Pipeline

1. Navigate to **DAGs** page in Airflow UI
2. Find `weather_etl_pipeline`
3. Toggle the switch to **ON** (enables scheduling)
4. Click the **▶ Play** button → **Trigger DAG**

**Monitor Execution:**
- Click on the DAG name to view execution details
- **Graph View**: Shows task dependencies and status
- **Grid View**: Shows historical runs
- **Gantt Chart**: Shows task durations

---

## Project Structure

```
etl-pipeline-for-weather-data-using-airflow-neuralnouman/
│
├── dags/                              # Airflow DAGs
│   ├── weather_etl_dag.py                # Main ETL pipeline DAG
│   ├── helpers.py                         # Helper functions (API, transform, load)
│   └── config/                            # DAG-specific configuration
│       └── cities_config.py               # City coordinates configuration
│
├── config/                             # Global configuration
│   ├── cities.py                          # Master cities configuration
│   └── logging_config.yaml                # Logging settings
│
├── sql/                                # SQL scripts
│   ├── create_tables.sql                  # Table creation DDL
│   ├── create_views.sql                   # Data quality view
│   ├── create_indexes.sql                 # Performance indexes
│   └── sample_queries.sql                 # Useful queries for analysis
│
├── scripts/                            # Utility scripts
│   ├── init_db.sql                        # Database initialization
│   ├── test_connection.py                 # Connection test script
│   ├── check_db_connection.py             # Database health check
│   └── cleanup_old_data.py                # Data retention script
│
├── tests/                              # Test suite
│   ├── test_extract.py                    # Extract phase tests
│   ├── test_transform.py                  # Transform phase tests
│   ├── test_load.py                       # Load phase tests
│   └── test_integration.py                # End-to-end tests
│
├── notebooks/                          # Jupyter notebooks
│   ├── data_exploration.ipynb             # Data analysis notebook
│   └── pipeline_monitoring.ipynb          # Monitoring dashboard
│
├── docs/                               # Documentation
│   ├── setup_guide.md                     # Detailed setup instructions
│   ├── architecture.md                    # Architecture deep dive
│   ├── troubleshooting.md                 # Common issues and solutions
│   └── api_documentation.md               # API reference
│
├── docker/                             # Docker configuration
│   └── Dockerfile                         # Custom Airflow image
│
├── logs/                               # Airflow logs (auto-generated)
├── plugins/                            # Custom Airflow plugins
│
├── docker-compose.yml                  # Docker services orchestration
├── requirements.txt                    # Python dependencies
├── pytest.ini                          # Test configuration
├── README.md                           # This file
├── PROJECT_SUMMARY.md                  # Project summary
├── QUICK_START.md                      # Quick start guide
├── airflow_etl_runs.png               # Pipeline execution screenshot
└── graph_result.png                   # Pipeline graph visualization
```

---

## Database Schema

### weather_records Table

Stores raw weather data extracted from the API.

| Column                  | Type           | Constraints                    | Description                          |
|------------------------|----------------|--------------------------------|--------------------------------------|
| `id`                   | SERIAL         | PRIMARY KEY                    | Unique record identifier             |
| `city`                 | VARCHAR(100)   | NOT NULL                       | City name                            |
| `latitude`             | DECIMAL(10,6)  | NOT NULL                       | Latitude coordinate                  |
| `longitude`            | DECIMAL(10,6)  | NOT NULL                       | Longitude coordinate                 |
| `temperature_celsius`  | DECIMAL(5,2)   | CHECK (-100 to 100)            | Temperature in Celsius               |
| `temperature_fahrenheit`| DECIMAL(5,2)  |                                | Converted temperature in Fahrenheit  |
| `humidity`             | DECIMAL(5,2)   | CHECK (0 to 100)               | Relative humidity percentage         |
| `wind_speed`           | DECIMAL(5,2)   | CHECK (>= 0)                   | Wind speed in m/s                    |
| `weather_condition`    | VARCHAR(100)   |                                | Weather description (Clear, Cloudy)  |
| `timestamp`            | TIMESTAMP      | NOT NULL                       | Weather measurement timestamp        |
| `extraction_date`      | TIMESTAMP      | DEFAULT CURRENT_TIMESTAMP      | Data extraction timestamp            |
| `created_at`           | TIMESTAMP      | DEFAULT CURRENT_TIMESTAMP      | Record creation timestamp            |

**Indexes:**
- `idx_city_timestamp` on (`city`, `timestamp`)
- `idx_extraction_date` on (`extraction_date`)

### daily_weather_stats Table

Stores aggregated daily statistics per city.

| Column                  | Type         | Constraints        | Description                      |
|------------------------|--------------|--------------------|----------------------------------|
| `id`                   | SERIAL       | PRIMARY KEY        | Unique record identifier         |
| `city`                 | VARCHAR(100) | NOT NULL           | City name                        |
| `date`                 | DATE         | NOT NULL           | Date of statistics               |
| `avg_temp_celsius`     | DECIMAL(5,2) |                    | Average temperature (°C)         |
| `avg_temp_fahrenheit`  | DECIMAL(5,2) |                    | Average temperature (°F)         |
| `max_temp_celsius`     | DECIMAL(5,2) |                    | Maximum temperature (°C)         |
| `max_temp_fahrenheit`  | DECIMAL(5,2) |                    | Maximum temperature (°F)         |
| `min_temp_celsius`     | DECIMAL(5,2) |                    | Minimum temperature (°C)         |
| `min_temp_fahrenheit`  | DECIMAL(5,2) |                    | Minimum temperature (°F)         |
| `avg_humidity`         | DECIMAL(5,2) |                    | Average humidity (%)             |
| `avg_wind_speed`       | DECIMAL(5,2) |                    | Average wind speed (m/s)         |
| `created_at`           | TIMESTAMP    | DEFAULT NOW()      | Record creation timestamp        |

**Constraints:**
- `UNIQUE(city, date)` - Prevents duplicate statistics

### v_data_quality_dashboard View

Provides data quality metrics for monitoring.

| Column                   | Description                                    |
|--------------------------|------------------------------------------------|
| `date`                   | Date of data collection                        |
| `total_records`          | Total number of records                        |
| `cities_count`           | Number of unique cities                        |
| `missing_temperature`    | Count of null temperature values               |
| `missing_humidity`       | Count of null humidity values                  |
| `missing_wind_speed`     | Count of null wind speed values                |
| `invalid_temperature`    | Count of out-of-range temperatures             |
| `invalid_humidity`       | Count of out-of-range humidity values          |
| `data_completeness_pct`  | Percentage of complete records                 |

---

## Configuration

### Cities Configuration

Edit `config/cities.py` to customize the cities tracked:

```python
CITIES = [
    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093},
    {"name": "Dubai", "latitude": 25.2048, "longitude": 55.2708},
    {"name": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Toronto", "latitude": 43.6532, "longitude": -79.3832},
    {"name": "Berlin", "latitude": 52.5200, "longitude": 13.4050},
]
```

### Schedule Configuration

Modify the DAG schedule in `dags/weather_etl_dag.py`:

```python
@dag(
    dag_id='weather_etl_pipeline',
    schedule_interval='@daily',  # Options: @hourly, @daily, @weekly, or cron
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
```

**Common Schedule Intervals:**
- `'@hourly'` - Run every hour
- `'@daily'` - Run once per day at midnight
- `'@weekly'` - Run once per week
- `'0 */6 * * *'` - Every 6 hours (cron expression)
- `None` - Manual triggering only

### Retry Configuration

Adjust retry logic in `default_args`:

```python
default_args = {
    'retries': 3,                           # Number of retry attempts
    'retry_delay': timedelta(minutes=5),    # Wait time between retries
    'retry_exponential_backoff': True,      # Exponential backoff
    'max_retry_delay': timedelta(hours=1),  # Maximum retry delay
}
```

---

## Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_extract.py -v

# Run with coverage report
pytest tests/ --cov=dags --cov-report=html
```

### Test Database Connection

```bash
# Test PostgreSQL connection
python scripts/test_connection.py

# Check database health
python scripts/check_db_connection.py
```

### Test API Connection

```bash
# Test Open-Meteo API
curl "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
```

### Query Weather Data

```bash
# Connect to PostgreSQL
docker exec -it etl-pipeline-for-weather-data-using-airflow-neuralnouman-postgres-1 psql -U weather_user -d weather_data

# Run sample queries
SELECT city, temperature_celsius, humidity 
FROM weather_records 
ORDER BY extraction_date DESC 
LIMIT 10;

SELECT * FROM v_data_quality_dashboard;
```

---

## Monitoring & Observability

### Jupyter Notebooks

#### Data Exploration Notebook
```bash
# Launch Jupyter
jupyter notebook notebooks/data_exploration.ipynb
```

Features:
- Query and visualize weather data
- Temperature trend analysis
- City-wise comparisons
- Statistical summaries

#### Pipeline Monitoring Notebook
```bash
# Launch monitoring dashboard
jupyter notebook notebooks/pipeline_monitoring.ipynb
```

Features:
- Data quality metrics
- Pipeline execution history
- Completeness tracking
- Health status reports

### Airflow UI Views

1. **Graph View**: Visual DAG structure with task dependencies
2. **Grid View**: Historical runs and task status
3. **Gantt Chart**: Task duration analysis
4. **Calendar View**: Schedule visualization
5. **Code View**: DAG source code

### Log Monitoring

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
docker-compose logs -f postgres

# View task-specific logs in Airflow UI
# Navigate to: DAG → Run → Task → Logs
```

---

## Troubleshooting

### Common Issues

#### 1. Airflow Webserver Not Starting

```bash
# Check logs
docker-compose logs airflow-webserver

# Restart services
docker-compose restart airflow-webserver

# If persists, rebuild
docker-compose down
docker-compose up -d --build
```

#### 2. Database Connection Failed

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify database exists
docker exec -it etl-pipeline-for-weather-data-using-airflow-neuralnouman-postgres-1 psql -U airflow -l

# Test connection
python scripts/test_connection.py
```

#### 3. DAG Not Appearing in UI

```bash
# Check for Python syntax errors
docker exec -it etl-pipeline-for-weather-data-using-airflow-neuralnouman-airflow-scheduler-1 \
  python /opt/airflow/dags/weather_etl_dag.py

# Refresh DAG
docker-compose restart airflow-scheduler

# Check DAG parsing errors in Airflow UI
# Navigate to: Browse → DAG Runs → Import Errors
```

#### 4. Task Failures

```bash
# View task logs in Airflow UI
# Click on failed task → View Logs

# Common causes:
# - API rate limiting → Increase retry delay
# - Network timeout → Increase request timeout
# - Database locked → Check concurrent operations
```

#### 5. Permission Denied Errors

```bash
# Fix directory permissions
chmod -R 777 logs/
chmod -R 777 plugins/

# Or set correct AIRFLOW_UID
echo "AIRFLOW_UID=$(id -u)" > .env
docker-compose down
docker-compose up -d
```

---

## Cleanup & Maintenance

### Stop Services

```bash
# Stop all containers (preserves data)
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Data Retention

```bash
# Clean old data (keeps last 30 days)
python scripts/cleanup_old_data.py --days 30

# Manual cleanup
docker exec -it etl-pipeline-for-weather-data-using-airflow-neuralnouman-postgres-1 \
  psql -U weather_user -d weather_data -c \
  "DELETE FROM weather_records WHERE extraction_date < CURRENT_DATE - INTERVAL '30 days';"
```

### View Resource Usage

```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Clean unused Docker resources
docker system prune -a
```

---

## Advanced Features

### Dynamic Task Mapping

The pipeline uses Airflow 2.8+ dynamic task mapping for parallel city processing:

```python
@task
def extract_weather_for_city(city_info: Dict[str, Any]) -> Dict[str, Any]:
    # Process single city
    pass

# Map over all cities
extracted_data = extract_weather_for_city.expand(city_info=CITIES)
```

### Task Groups

Organized into logical groups for better visualization:

```python
@task_group(group_id='extract_weather_data')
def extract_group():
    # All extraction tasks
    pass
```

### XCom for Data Passing

Tasks communicate via XCom for data flow:

```python
# Push data
return {"city": "New York", "temp": 25}

# Pull data in downstream task
@task
def process_data(upstream_data):
    print(upstream_data['city'])
```

---

## API Reference

### Open-Meteo Weather API

**Endpoint:** `https://api.open-meteo.com/v1/forecast`

**Parameters:**
- `latitude`: Latitude coordinate (-90 to 90)
- `longitude`: Longitude coordinate (-180 to 180)
- `current`: Weather variables (comma-separated)
  - `temperature_2m`: Temperature at 2 meters
  - `relative_humidity_2m`: Relative humidity
  - `wind_speed_10m`: Wind speed at 10 meters
  - `weather_code`: WMO weather code

**Rate Limits:**
- 10,000 requests per day (free tier)
- Consider implementing caching for production

**Documentation:** [Open-Meteo Docs](https://open-meteo.com/en/docs)

---

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_city_date ON weather_records(city, DATE(extraction_date));

-- Analyze tables for query planning
ANALYZE weather_records;
ANALYZE daily_weather_stats;
```

### Airflow Optimization

```python
# Increase parallelism in airflow.cfg
[core]
parallelism = 32
dag_concurrency = 16
max_active_runs_per_dag = 3

# Use pools for resource management
[scheduler]
max_threads = 4
```

### Docker Resource Limits

```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/etl-pipeline-for-weather-data-using-airflow.git
cd etl-pipeline-for-weather-data-using-airflow-neuralnouman

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install black flake8 isort pytest pytest-cov
```

### Code Style

```bash
# Format code
black dags/ tests/

# Sort imports
isort dags/ tests/

# Lint code
flake8 dags/ tests/
```

### Commit Guidelines

```bash
# Feature
git commit -m "feat: add support for weather alerts"

# Bug fix
git commit -m "fix: resolve database connection timeout"

# Documentation
git commit -m "docs: update setup instructions"
```

### Pull Request Process

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes and commit: `git commit -m "feat: add amazing feature"`
3. Run tests: `pytest tests/ -v`
4. Push to your fork: `git push origin feature/amazing-feature`
5. Open a Pull Request with detailed description

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Muhammad Nouman Hafeez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## Acknowledgments

### Technologies Used
- **Apache Airflow** - Workflow orchestration
- **PostgreSQL** - Database management
- **Docker** - Containerization
- **Open-Meteo** - Free weather API
- **Python** - Core programming language

### Educational Resources
- [Airflow TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### Course Information
- **Course**: MLOps - Fall 2025
- **Institution**: [Your University Name]
- **Assignment**: Weather ETL Pipeline Implementation

---

## Author

**Muhammad Nouman Hafeez**
- GitHub: [@neuralnouman](https://github.com/neuralnouman)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

---

## Support

### Getting Help

- **Documentation**: Check the `docs/` folder for detailed guides
- **Issues**: [Open an issue](https://github.com/YOUR_USERNAME/etl-pipeline-for-weather-data-using-airflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/etl-pipeline-for-weather-data-using-airflow/discussions)

### Useful Commands Cheat Sheet

```bash
# Start pipeline
docker-compose up -d

# View logs
docker-compose logs -f

# Stop pipeline
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Access PostgreSQL
docker exec -it etl-pipeline-for-weather-data-using-airflow-neuralnouman-postgres-1 \
  psql -U weather_user -d weather_data

# Run tests
pytest tests/ -v

# Check Airflow version
docker exec -it etl-pipeline-for-weather-data-using-airflow-neuralnouman-airflow-scheduler-1 \
  airflow version
```

---

<div align="center">

### Star this repository if you find it helpful!

**Built with dedication for MLOps learning and production-ready data pipelines**

[Back to Top](#weather-etl-pipeline-using-apache-airflow)

</div>
