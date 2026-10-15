"""HireScope batch pipeline: CSV -> Bronze -> Silver -> Postgres -> dbt."""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON = "/home/airflow/venv/bin/python"
DBT = "/home/airflow/venv/bin/dbt"
PROJECT = "/opt/project"
DBT_DIR = f"{PROJECT}/dbt/hirescope"

# dbt writes its build artefacts to /tmp so the mounted project folder stays clean.
DBT_ENV = {"DBT_TARGET_PATH": "/tmp/dbt_target", "DBT_LOG_PATH": "/tmp/dbt_logs"}

with DAG(
    dag_id="hirescope_pipeline",
    description="CSV -> Bronze (Parquet) -> Silver (PySpark) -> Postgres -> dbt star schema",
    start_date=datetime(2026, 1, 1),
    schedule=None,  # single-snapshot dataset: trigger manually
    catchup=False,
    is_paused_upon_creation=False,
    default_args={"owner": "hirescope", "retries": 1},
    tags=["hirescope"],
) as dag:

    ingest_bronze = BashOperator(
        task_id="ingest_bronze",
        bash_command=f"{PYTHON} {PROJECT}/src/ingest_bronze.py",
    )

    process_silver = BashOperator(
        task_id="process_silver",
        bash_command=f"{PYTHON} {PROJECT}/src/process_silver.py",
    )

    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command=f"{PYTHON} {PROJECT}/src/load_postgres.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && {DBT} run --profiles-dir {DBT_DIR}",
        env=DBT_ENV,
        append_env=True,
    )

    dbt_docs = BashOperator(
        task_id="dbt_docs",
        bash_command=f"cd {DBT_DIR} && {DBT} docs generate --profiles-dir {DBT_DIR}",
        env=DBT_ENV,
        append_env=True,
    )

    ingest_bronze >> process_silver >> load_postgres >> dbt_run >> dbt_docs
