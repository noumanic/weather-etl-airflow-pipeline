# Weather ETL Pipeline - Architecture

## System Overview

The Weather ETL Pipeline is a production-grade data engineering solution that extracts weather data from the Open-Meteo API, transforms it, and loads it into a PostgreSQL database using Apache Airflow for orchestration.

## Architecture Diagram

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

## Component Details

### 1. Data Source: Open-Meteo API

**Purpose**: Provides free, real-time weather data without requiring an API key.

**Features**:
- Global coverage
- Current weather conditions
- No rate limiting (fair use)
- ISO 8601 timestamps
- WMO weather codes

**Data Points Extracted**:
- Temperature (°C)
- Relative humidity (%)
- Wind speed (m/s)
- Weather condition code
- Measurement timestamp

### 2. Orchestration: Apache Airflow

**Purpose**: Schedules, monitors, and manages the ETL pipeline.

**Key Features**:
- **TaskFlow API**: Modern, Pythonic DAG definition
- **Task Groups**: Logical organization of related tasks
- **Retry Logic**: Automatic retry on failure (3 attempts)
- **Dependency Management**: Clear task dependencies
- **Monitoring**: Web UI for tracking pipeline execution

**Airflow Components**:
- **Scheduler**: Triggers DAG runs on schedule
- **Webserver**: Provides UI and REST API
- **Executor**: LocalExecutor for task execution
- **Database**: PostgreSQL for Airflow metadata

### 3. Extract Layer

**Purpose**: Fetch weather data from Open-Meteo API for multiple cities.

**Implementation**:
```python
@task_group(group_id='extract_weather_data')
def extract_group():
    @task(retries=3, retry_delay=timedelta(minutes=2))
    def extract_weather_for_city(city_info):
        # API call implementation
        pass
    
    return [extract_weather_for_city(city) for city in CITIES]
```

**Features**:
- **Parallel Execution**: Each city extracted concurrently
- **Error Handling**: Retries with exponential backoff
- **Timeout Management**: 10-second timeout per request
- **Logging**: Detailed logs for debugging

**Error Handling**:
- Network timeouts
- API unavailability
- Invalid responses
- Rate limiting (if encountered)

### 4. Transform Layer

**Purpose**: Clean, enrich, and aggregate the raw weather data.

**Transformations**:

1. **Temperature Conversion**
   ```python
   fahrenheit = (celsius * 9/5) + 32
   ```

2. **Timestamp Addition**
   - Add extraction timestamp
   - Format timestamps consistently (ISO 8601)

3. **Daily Statistics Calculation**
   - Average temperature (both scales)
   - Min/max temperatures
   - Average humidity and wind speed
   - City count

**Data Quality Checks**:
- Null value detection
- Range validation (temperature, humidity)
- Conversion accuracy verification

### 5. Load Layer

**Purpose**: Persist transformed data to PostgreSQL database.

**Tables**:

1. **weather_records**
   - Raw weather measurements
   - Includes both Celsius and Fahrenheit
   - Indexed for fast querying

2. **daily_weather_stats**
   - Aggregated daily statistics
   - One record per city per day
   - UPSERT logic (ON CONFLICT UPDATE)

3. **etl_audit_log**
   - Pipeline execution history
   - Performance metrics
   - Error tracking

**Database Features**:
- **Transactions**: ACID compliance
- **Indexes**: Optimized for common queries
- **Constraints**: Data integrity checks
- **Views**: Pre-built analytical queries

### 6. Validation Layer

**Purpose**: Ensure data quality and integrity.

**Quality Checks**:
1. Record count validation
2. Null value detection
3. Temperature range validation (-50°C to 60°C)
4. Conversion accuracy (Celsius ↔ Fahrenheit)
5. Humidity range validation (0-100%)
6. Statistics completeness check

**Output**: Boolean pass/fail + detailed messages

### 7. Notification Layer

**Purpose**: Inform stakeholders of pipeline completion.

**Current Implementation**: Logging to console

**Future Enhancements**:
- Email notifications
- Slack integration
- SMS alerts
- Dashboard updates

## Data Flow

### Detailed Data Flow

1. **Trigger**
   - Scheduled (daily at midnight)
   - Manual trigger from UI
   - CLI trigger

2. **Extract Phase**
   ```
   For each city:
     → Call API
     → Parse JSON response
     → Extract relevant fields
     → Return weather dictionary
   ```

3. **Transform Phase**
   ```
   For each weather record:
     → Convert temperature to Fahrenheit
     → Add extraction timestamp
     → Validate data ranges
   
   Aggregate:
     → Calculate daily statistics
     → Compute averages, min, max
   ```

4. **Load Phase**
   ```
   Transaction start:
     → Insert weather records
     → Insert daily statistics
   Transaction commit
   ```

5. **Validate Phase**
   ```
   Run quality checks:
     → Verify record count
     → Check for nulls
     → Validate ranges
     → Confirm conversions
   Return: pass/fail + messages
   ```

6. **Notify Phase**
   ```
   Generate report:
     → Summarize execution
     → Include statistics
     → Log completion
   ```

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Orchestration | Apache Airflow | 2.8.0 | Workflow management |
| Database | PostgreSQL | 15 | Data storage |
| Language | Python | 3.11+ | Implementation |
| Containerization | Docker | 20.10+ | Deployment |
| Container Orchestration | Docker Compose | 2.0+ | Service management |

### Python Libraries

| Library | Purpose |
|---------|---------|
| apache-airflow | Workflow orchestration |
| apache-airflow-providers-postgres | PostgreSQL integration |
| requests | HTTP API calls |
| psycopg2-binary | PostgreSQL driver |
| pandas | Data analysis (notebooks) |
| pytest | Unit testing |

## Scalability Considerations

### Current Limitations

- **Executor**: LocalExecutor (single machine)
- **Parallelism**: Limited by CPU cores
- **Cities**: 10 cities currently supported

### Scaling Options

1. **Horizontal Scaling**
   - Switch to CeleryExecutor or KubernetesExecutor
   - Add worker nodes
   - Distribute task execution

2. **Vertical Scaling**
   - Increase CPU/RAM
   - Optimize database queries
   - Add database read replicas

3. **Data Partitioning**
   - Partition tables by date
   - Archive old data
   - Implement data retention policies

## Security

### Current Implementation

- Database credentials in environment variables
- No API key required (Open-Meteo)
- Local network only (not exposed to internet)

### Production Recommendations

- Use secret management (AWS Secrets Manager, HashiCorp Vault)
- Enable SSL for PostgreSQL
- Implement authentication for Airflow UI
- Use RBAC for user permissions
- Encrypt sensitive data at rest

## Monitoring and Observability

### Built-in Monitoring

1. **Airflow UI**
   - DAG execution status
   - Task duration
   - Failure notifications
   - Log viewer

2. **Database Views**
   - `v_data_quality_dashboard`
   - `v_pipeline_performance`
   - `etl_audit_log` table

3. **Logs**
   - Task logs in Airflow
   - Container logs via Docker

### Future Enhancements

- Prometheus metrics export
- Grafana dashboards
- Alert manager integration
- Custom metrics tracking

## Disaster Recovery

### Backup Strategy

1. **Database Backups**
   ```bash
   # Daily automated backups
   pg_dump weather_data > backup_$(date +%Y%m%d).sql
   ```

2. **Configuration Backups**
   - DAG files in version control
   - Environment variables documented
   - Database schema scripts

### Recovery Procedures

1. **Database Recovery**
   ```bash
   psql weather_data < backup_20240101.sql
   ```

2. **DAG Recovery**
   - Pull from version control
   - Redeploy containers

3. **Data Replay**
   - Airflow supports backfilling
   - Can rerun historical DAG runs

## Performance Optimization

### Current Optimizations

1. **Database**
   - Indexes on frequently queried columns
   - Views for common queries
   - Connection pooling

2. **API Calls**
   - Parallel execution per city
   - Timeouts to prevent hanging
   - Retry logic for failures

3. **Code**
   - Helper functions for reusability
   - Minimal data copying
   - Efficient data structures

### Future Optimizations

- Caching for API responses
- Batch processing for database inserts
- Asynchronous task execution
- Query optimization based on execution plans

## Maintenance

### Regular Tasks

1. **Daily**
   - Monitor DAG runs
   - Check data quality

2. **Weekly**
   - Review logs for errors
   - Check disk space

3. **Monthly**
   - Clean up old logs
   - Archive old data
   - Update dependencies

4. **Quarterly**
   - Review and optimize queries
   - Update documentation
   - Security audit
