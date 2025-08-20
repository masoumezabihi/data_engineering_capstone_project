from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta, date
from pathlib import Path
import yfinance as yf
import pandas as pd

BASE_PATH = "/opt/airflow"

def download_market_data(stock_symbol):
    start_date = date.today()
    end_date = start_date + timedelta(days=1)
    stock_df = yf.download(stock_symbol, start=start_date, end=end_date, interval='1m')

    filename = Path(BASE_PATH) / f"data_{stock_symbol}.csv"
    stock_df.to_csv(filename, header=False)

def run_query(execution_date):
    path = Path(f"/tmp/data/{execution_date}/")

    try:
        aapl = pd.read_csv(path / "data_AAPL.csv", header=None,
                           names=['date_time', 'open', 'high', 'low', 'close', 'volume'])
        tsla = pd.read_csv(path / "data_TSLA.csv", header=None,
                           names=['date_time', 'open', 'high', 'low', 'close', 'volume'])
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print("AAPL Max Close:", aapl['close'].max())
    print("TSLA Max Close:", tsla['close'].max())

default_args = {
    'owner': 'dataengineer',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 8, 20)
}

dag = DAG(
    dag_id='marketvol',
    default_args=default_args,
    description='Download stock data and analyze',
    schedule_interval='0 18 * * 1-5',
)

t0 = BashOperator(
    task_id='create_temp_directory',
    bash_command='mkdir -p /tmp/data/{{ ds }}',
    dag=dag
)

t1 = PythonOperator(
    task_id='download_market_data_aapl',
    python_callable=download_market_data,
    op_kwargs={'stock_symbol': 'AAPL'},
    dag=dag
)

t2 = PythonOperator(
    task_id='download_market_data_tsla',
    python_callable=download_market_data,
    op_kwargs={'stock_symbol': 'TSLA'},
    dag=dag
)

t3 = BashOperator(
    task_id='move_aapl_data_to_temp_directory',
    bash_command=f'mv {BASE_PATH}/data_AAPL.csv /tmp/data/{{{{ ds }}}}/',
    dag=dag
)

t4 = BashOperator(
    task_id='move_tsla_data_to_temp_directory',
    bash_command=f'mv {BASE_PATH}/data_TSLA.csv /tmp/data/{{{{ ds }}}}/',
    dag=dag
)

t5 = PythonOperator(
    task_id='run_query',
    python_callable=run_query,
    op_kwargs={'execution_date': '{{ ds }}'},
    dag=dag
)

t0 >> [t1, t2]
t1 >> t3
t2 >> t4
[t3, t4] >> t5
