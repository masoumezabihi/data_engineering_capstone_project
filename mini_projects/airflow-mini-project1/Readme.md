# MarketVol Airflow DAG

This DAG downloads 1-minute stock data for **AAPL** and **TSLA** from Yahoo Finance, stores it, and computes the **maximum close price** for both stocks.

## How to Run

### 1. Copy the DAG
Place the DAG file `dag_marketvol.py` into your Airflow 'dags/' folder. If you're using Docker, you can copy the file in ('/opt/airflow/dags/')

### 2. Access the Airflow Web UI
If no users exist yet, you can create an admin user or any other user (e.g., airflow) using the following command inside the Airflow webserver container:
docker exec -it airflow-webserver airflow users create \
  --username airflow \
  --firstname Firstname \
  --lastname Lastname \
  --role Admin \
  --email airflow@example.com \
  --password airflow
Replace the values as needed. Once created, log in using the credentials at the URL above.

### 3. Enable and Trigger the DAG
 - Find the DAG named marketvol in DAGS
 - Toggle it on
 - Click the ▶️ Trigger DAG button to run it manually

## Output Location
The stock data is saved and moved to: /tmp/data/<execution_date>/
Each CSV file is named:
  - data_AAPL.csv
  - data_TSLA.csv
## DAG Schedule
This DAG is scheduled to run Monday–Friday at 18:00 UTC.

## Dependencies
This DAG uses:
  - yfinance
  - pandas
Make sure these are installed inside your Airflow environment.
