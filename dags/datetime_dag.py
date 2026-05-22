import datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

with DAG(
    dag_id="datetime_dag",
    start_date=datetime.datetime(2026, 1, 1),
    schedule="@daily",
):
    EmptyOperator(task_id="datetime_task")