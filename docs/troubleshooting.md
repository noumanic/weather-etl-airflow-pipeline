# Troubleshooting Guide

Common issues and their solutions for the Weather ETL Pipeline.

## Table of Contents

1. [Docker Issues](#docker-issues)
2. [Airflow Issues](#airflow-issues)
3. [Database Issues](#database-issues)
4. [DAG Issues](#dag-issues)
5. [API Issues](#api-issues)
6. [Performance Issues](#performance-issues)

## Docker Issues

### Docker Desktop not starting

**Symptoms:**
- Docker commands fail
- "Cannot connect to the Docker daemon" error

**Solutions:**

1. **Restart Docker Desktop**
   ```bash
   # Windows: Restart from System Tray
   # Mac: Restart from Menu Bar
   # Linux:
   sudo systemctl restart docker
   ```

2. **Check WSL2 (Windows)**
   ```bash
   wsl --list --verbose
   # Ensure WSL2 is installed and set as default
   wsl --set-default-version 2
   ```

3. **Reset Docker Desktop**
   - Settings → Troubleshoot → Reset to factory defaults

### Containers won't start

**Symptoms:**
- `docker-compose up` fails
- Containers exit immediately

**Solutions:**

1. **Check logs**
   ```bash
   docker-compose logs
   docker-compose logs [service-name]
   ```

2. **Check ports**
   ```bash
   # Ensure ports 8080 and 5432 are available
   netstat -ano | findstr :8080
   netstat -ano | findstr :5432
   ```

3. **Clean and rebuild**
   ```bash
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Out of disk space

**Symptoms:**
- "no space left on device" error
- Slow container performance

**Solutions:**

1. **Clean up Docker resources**
   ```bash
   # Remove unused containers, networks, images
   docker system prune -a
   
   # Remove volumes
   docker volume prune
   ```

2. **Clean up logs**
   ```bash
   # Remove old Airflow logs
   find logs/ -name "*.log" -mtime +30 -delete
   ```

3. **Clean up old data**
   ```bash
   python scripts/cleanup_old_data.py --retention-days 90 --execute
   ```

## Airflow Issues

### Airflow webserver not accessible

**Symptoms:**
- Cannot access http://localhost:8080
- "Connection refused" error

**Solutions:**

1. **Check container status**
   ```bash
   docker-compose ps
   # airflow-webserver should be "Up (healthy)"
   ```

2. **Check webserver logs**
   ```bash
   docker-compose logs airflow-webserver
   # Look for errors
   ```

3. **Restart webserver**
   ```bash
   docker-compose restart airflow-webserver
   # Wait 30 seconds
   ```

4. **Check health**
   ```bash
   curl http://localhost:8080/health
   # Should return healthy status
   ```

### Cannot login to Airflow UI

**Symptoms:**
- "Invalid username or password" error

**Solutions:**

1. **Verify credentials**
   - Check `.env` file
   - Default: username=airflow, password=airflow

2. **Reset admin user**
   ```bash
   docker exec -it <airflow-webserver-container> \
     airflow users delete --username airflow
   
   docker exec -it <airflow-webserver-container> \
     airflow users create \
       --username airflow \
       --password airflow \
       --firstname Admin \
       --lastname User \
       --role Admin \
       --email admin@example.com
   ```

3. **Clear browser cache**
   - Clear cookies and cache for localhost:8080

### Scheduler not processing DAGs

**Symptoms:**
- DAG runs not starting
- Tasks stuck in "scheduled" state

**Solutions:**

1. **Check scheduler logs**
   ```bash
   docker-compose logs airflow-scheduler | tail -100
   ```

2. **Restart scheduler**
   ```bash
   docker-compose restart airflow-scheduler
   ```

3. **Check scheduler health**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     airflow jobs check --job-type SchedulerJob
   ```

4. **Force DAG parse**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     airflow dags reserialize
   ```

## Database Issues

### Cannot connect to PostgreSQL

**Symptoms:**
- "Connection refused" error
- "could not connect to server" error

**Solutions:**

1. **Check PostgreSQL container**
   ```bash
   docker-compose ps postgres
   # Should be "Up (healthy)"
   ```

2. **Test connection**
   ```bash
   docker exec -it <postgres-container> \
     psql -U weather_user -d weather_data -c "SELECT 1"
   ```

3. **Check PostgreSQL logs**
   ```bash
   docker-compose logs postgres | tail -50
   ```

4. **Verify connection parameters**
   - Host: postgres (inside Docker) or localhost (from host)
   - Port: 5432
   - Database: weather_data
   - User: weather_user
   - Password: weather_pass

### Database does not exist

**Symptoms:**
- "database 'weather_data' does not exist" error

**Solutions:**

1. **Recreate database**
   ```bash
   docker exec -it <postgres-container> \
     psql -U airflow -c "CREATE DATABASE weather_data"
   ```

2. **Run initialization script**
   ```bash
   docker exec -it <postgres-container> \
     psql -U airflow -d weather_data -f /docker-entrypoint-initdb.d/init_db.sql
   ```

3. **Complete rebuild**
   ```bash
   docker-compose down -v
   docker-compose up -d
   # This will recreate everything including the database
   ```

### Tables do not exist

**Symptoms:**
- "relation 'weather_records' does not exist" error

**Solutions:**

1. **Run table creation script**
   ```bash
   docker exec -it <postgres-container> \
     psql -U weather_user -d weather_data -f /opt/airflow/sql/create_tables.sql
   ```

2. **Verify tables**
   ```bash
   docker exec -it <postgres-container> \
     psql -U weather_user -d weather_data -c "\dt"
   ```

### Permission denied errors

**Symptoms:**
- "permission denied for table weather_records" error

**Solutions:**

1. **Grant permissions**
   ```bash
   docker exec -it <postgres-container> \
     psql -U airflow -d weather_data -c "
       GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weather_user;
       GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO weather_user;
     "
   ```

## DAG Issues

### DAG not appearing in UI

**Symptoms:**
- DAG missing from DAG list
- No import errors shown

**Solutions:**

1. **Check for syntax errors**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     python /opt/airflow/dags/weather_etl_dag.py
   ```

2. **Check import errors**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     airflow dags list-import-errors
   ```

3. **Check DAG file location**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     ls -la /opt/airflow/dags/
   ```

4. **Restart scheduler**
   ```bash
   docker-compose restart airflow-scheduler
   ```

### DAG import errors

**Symptoms:**
- "Broken DAG" message in UI
- Import errors shown

**Solutions:**

1. **Check error message**
   - Go to Airflow UI → DAGs
   - Click on import errors link
   - Read the error message

2. **Common import errors:**

   **Missing module:**
   ```bash
   # Install missing package
   docker exec -it <airflow-scheduler-container> \
     pip install <package-name>
   ```

   **Python path issues:**
   ```python
   # Add to DAG file
   import sys
   import os
   sys.path.insert(0, os.path.dirname(__file__))
   ```

3. **Verify helpers module**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     ls -la /opt/airflow/dags/helpers.py
   ```

### Task failing repeatedly

**Symptoms:**
- Task shows red (failed) in UI
- All retries exhausted

**Solutions:**

1. **Check task logs**
   - Click on task in Graph View
   - Click "Log" button
   - Read error messages

2. **Common task failures:**

   **API timeout:**
   - Increase retry delay
   - Check internet connection
   - Verify API endpoint

   **Database error:**
   - Check database connection
   - Verify table exists
   - Check SQL syntax

   **Import error:**
   - Verify all dependencies installed
   - Check Python path
   - Restart scheduler

3. **Clear task and rerun**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     airflow tasks clear weather_etl_pipeline -t <task_id>
   ```

## API Issues

### API requests timing out

**Symptoms:**
- Extract tasks failing
- "Connection timeout" errors

**Solutions:**

1. **Test API manually**
   ```bash
   curl -v "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m"
   ```

2. **Check internet connectivity**
   ```bash
   docker exec -it <airflow-scheduler-container> \
     ping -c 3 api.open-meteo.com
   ```

3. **Increase timeout**
   ```python
   # In helpers.py
   response = requests.get(url, params=params, timeout=30)  # Increase from 10
   ```

4. **Check firewall**
   - Ensure outbound HTTPS (port 443) is allowed

### API returning unexpected data

**Symptoms:**
- Transform tasks failing
- "KeyError" or "None type" errors

**Solutions:**

1. **Log API response**
   ```python
   # Add to extract task
   logger.info(f"API Response: {response.json()}")
   ```

2. **Verify API parameters**
   - Check latitude/longitude values
   - Verify API parameters match documentation

3. **Handle missing data**
   ```python
   # Add defensive coding
   temperature = current.get('temperature_2m', None)
   if temperature is None:
       logger.warning(f"No temperature data for {city}")
   ```

### API rate limiting

**Symptoms:**
- "429 Too Many Requests" error
- Intermittent failures

**Solutions:**

1. **Add rate limiting**
   ```python
   import time
   
   # In extract function
   time.sleep(1)  # 1 second delay between requests
   ```

2. **Reduce frequency**
   - Change schedule from @hourly to @daily
   - Reduce number of cities

## Performance Issues

### DAG running slowly

**Symptoms:**
- Tasks take longer than expected
- Pipeline execution > 10 minutes

**Solutions:**

1. **Check task duration**
   - Go to Graph View
   - Click on task → Duration
   - Identify slow tasks

2. **Optimize slow tasks:**

   **Extract tasks:**
   - Ensure parallel execution
   - Increase timeout if needed
   - Check network latency

   **Transform tasks:**
   - Profile Python code
   - Optimize calculations
   - Reduce data copying

   **Load tasks:**
   - Use batch inserts
   - Add database indexes
   - Optimize SQL queries

3. **Check system resources**
   ```bash
   docker stats
   # Monitor CPU and memory usage
   ```

### Database queries slow

**Symptoms:**
- Load tasks taking minutes
- Query timeouts

**Solutions:**

1. **Add indexes**
   ```bash
   docker exec -it <postgres-container> \
     psql -U weather_user -d weather_data \
       -f /opt/airflow/sql/create_indexes.sql
   ```

2. **Analyze query performance**
   ```sql
   EXPLAIN ANALYZE SELECT * FROM weather_records WHERE city = 'New York';
   ```

3. **Optimize queries**
   - Use indexed columns in WHERE clauses
   - Avoid SELECT *
   - Use LIMIT for large result sets

4. **Vacuum database**
   ```bash
   docker exec -it <postgres-container> \
     psql -U weather_user -d weather_data -c "VACUUM ANALYZE"
   ```

### High memory usage

**Symptoms:**
- Docker consuming excessive RAM
- System slowdown

**Solutions:**

1. **Check container memory**
   ```bash
   docker stats --no-stream
   ```

2. **Limit Docker memory**
   - Docker Desktop → Settings → Resources
   - Reduce memory allocation

3. **Optimize DAG**
   - Process data in chunks
   - Don't load entire dataset in memory
   - Clean up intermediate results

## Getting Additional Help

If the issue persists after trying these solutions:

1. **Check Airflow logs**
   - Look for stack traces and error messages

2. **Review system logs**
   ```bash
   docker-compose logs --tail=200
   ```

3. **Enable debug logging**
   ```python
   # In DAG file
   import logging
   logging.getLogger().setLevel(logging.DEBUG)
   ```

4. **Create minimal reproducible example**
   - Isolate the failing component
   - Test independently

5. **Consult documentation**
   - Airflow: https://airflow.apache.org/docs/
   - Docker: https://docs.docker.com/
   - PostgreSQL: https://www.postgresql.org/docs/

6. **Community support**
   - Stack Overflow
   - Airflow Slack channel
   - GitHub issues
