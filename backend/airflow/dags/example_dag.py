from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def check_veda():
    print("Veda Orchestrator is running!")

with DAG('veda_health_check', start_date=datetime(2023, 1, 1), schedule_interval='@daily', catchup=False) as dag:
    task = PythonOperator(
        task_id='check_veda_status',
        python_callable=check_veda
    )
