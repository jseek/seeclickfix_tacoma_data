from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import json

# Database connection parameters
DB_CONN_PARAMS = {
    "dbname": "airflow",
    "user": "airflow",
    "password": "airflow",
    "host": "postgres",
    "port": 5432,
}

OUTPUT_FILE_PATH = "/opt/airflow/exports/seeclickfix_issues_dump.json"

def export_to_json():
    """Fetch all records from seeclickfix_issues, sort by ID, and save as JSON."""
    conn = psycopg2.connect(**DB_CONN_PARAMS)
    cursor = conn.cursor()

    query = "SELECT * FROM seeclickfix_issues ORDER BY id"
    cursor.execute(query)
    
    columns = [desc[0] for desc in cursor.description]
    records = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False, default=str)

    cursor.close()
    conn.close()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "export_seeclickfix_issues",
    default_args=default_args,
    description="Export seeclickfix_issues table to JSON after DAG completion",
    schedule_interval="@hourly",
    catchup=False,
)

export_task = PythonOperator(
    task_id="export_to_json",
    python_callable=export_to_json,
    dag=dag,
)

export_task
