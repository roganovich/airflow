import datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="log_generator_dag",
    start_date=datetime.datetime(2026, 1, 1),
    schedule="@daily",
    default_args={"retries": 2},
):
    op = BashOperator(
        task_id="log_generator_task",
        bash_command="python {{ dag.folder }}/scripts/log_generator.py --format apache --lines 10000 --dirty-percent 10 --verbose"
    )
