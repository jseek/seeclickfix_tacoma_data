from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta, timezone
import requests
import psycopg2
import logging
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Database connection parameters
DB_CONN_PARAMS = {
    "dbname": "airflow",
    "user": "airflow",
    "password": "airflow",
    "host": "postgres",
    "port": 5432,
}

# SeeClickFix API details
BASE_URL = "https://seeclickfix.com/api/v2/issues"
PLACE_URL = "tacoma"
PER_PAGE = 20  # SeeClickFix api limits records with details to 20
SLEEP_SECONDS = (60/20) # Time to wait between loops. SCF api limits to 20 requests every 60 seconds

# Default updated_at timestamp
DEFAULT_UPDATED_AT = "2024-01-01T00:00:00Z"
CREATED_AT_AFTER = "2024-01-01T00:00:00Z"

def get_updated_at():
    """Retrieve last updated timestamp from Airflow Variables."""
    return Variable.get("seeclickfix_last_updated", DEFAULT_UPDATED_AT)

def fetch_data(**kwargs):
    """Fetch data from SeeClickFix API with pagination and filtering."""
    updated_at = get_updated_at()
    page = 1
    issues = []
    total_entries = 0

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    while True:
        url = f"{BASE_URL}?place_url={PLACE_URL}&details=true&after={CREATED_AT_AFTER}&sort=updated_at&sort_direction=ASC&page={page}&per_page={PER_PAGE}&updated_at_after={updated_at}"

        logging.info(f"Fetching data from: {url}")
        response = session.get(url)
        time.sleep(SLEEP_SECONDS)
        data = response.json()

        if response.status_code != 200:
            logging.error(f"API error {response.status_code}: {data}")
            break

        if "issues" in data:
            issues.extend(data["issues"])
            total_entries = data.get("metadata", {}).get("pagination", {}).get("entries", 0)
            logging.info(f"Page {page}: Retrieved {len(data['issues'])} issues (Total: {len(issues)}/{total_entries})")

        # Check if there's a next page
        next_page = data.get("metadata", {}).get("pagination", {}).get("next_page")
        if not next_page:
            break
        page = next_page
    
    kwargs['ti'].xcom_push(key='issues', value=issues)
    
    # Store the latest updated_at timestamp for future runs
    if issues:
        latest_updated_at = max(datetime.fromisoformat(issue["updated_at"].replace("Z", "+00:00")) for issue in issues)
        latest_updated_at_utc = latest_updated_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        Variable.set("seeclickfix_last_updated", latest_updated_at_utc)
        logging.info(f"Updated latest timestamp to: {latest_updated_at_utc}")

def store_data(**kwargs):
    """Ensure table exists and store fetched issues in database."""
    ti = kwargs['ti']
    issues = ti.xcom_pull(task_ids='fetch_data', key='issues')
    if not issues:
        logging.info("No new issues to store.")
        return
    
    conn = psycopg2.connect(**DB_CONN_PARAMS)
    cursor = conn.cursor()

    # Ensure the table exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS seeclickfix_issues (
        id BIGINT PRIMARY KEY,
        description TEXT,
        status TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        lat DOUBLE PRECISION,
        lng DOUBLE PRECISION,
        acknowledged_at TIMESTAMP,
        address TEXT,
        closed_at TIMESTAMP,
        comment_url TEXT,
        comment_count INT,
        html_url TEXT,
        rating TEXT,
        shortened_url TEXT,
        summary TEXT,
        url TEXT,
        vote_count INT,
        votes TEXT,
        assignee_id BIGINT,
        assignee_name TEXT,
        assignee_role TEXT,
        reporter_id BIGINT,
        reporter_name TEXT,
        reporter_role TEXT,
        request_type_id BIGINT,
        request_type_title TEXT,
        request_type_organization TEXT
    );
    """
    cursor.execute(create_table_query)

    insert_query = """
    INSERT INTO seeclickfix_issues (id, description, status, created_at, updated_at, lat, lng, acknowledged_at, address, closed_at, comment_url, comment_count, html_url, rating, shortened_url, summary, url, vote_count, assignee_id, assignee_name, assignee_role, reporter_id, reporter_name, reporter_role, request_type_id, request_type_title, request_type_organization)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at,
    acknowledged_at = EXCLUDED.acknowledged_at,
    address = EXCLUDED.address,
    closed_at = EXCLUDED.closed_at,
    comment_url = EXCLUDED.comment_url,
    comment_count = EXCLUDED.comment_count,
    html_url = EXCLUDED.html_url,
    rating = EXCLUDED.rating,
    shortened_url = EXCLUDED.shortened_url,
    summary = EXCLUDED.summary,
    url = EXCLUDED.url,
    vote_count = EXCLUDED.vote_count,
    assignee_id = EXCLUDED.assignee_id,
    assignee_name = EXCLUDED.assignee_name,
    assignee_role = EXCLUDED.assignee_role,
    reporter_id = EXCLUDED.reporter_id,
    reporter_name = EXCLUDED.reporter_name,
    reporter_role = EXCLUDED.reporter_role,
    request_type_id = EXCLUDED.request_type_id,
    request_type_title = EXCLUDED.request_type_title,
    request_type_organization = EXCLUDED.request_type_organization;
    """
    
    for issue in issues:
        try:
            assignee = issue.get("assignee", {})
            reporter = issue.get("reporter", {})
            request_type = issue.get("request_type", {})
            values = (
                issue.get("id"),
                issue.get("description", ""),
                issue.get("status", ""),
                issue.get("created_at"),
                issue.get("updated_at"),
                issue.get("lat"),
                issue.get("lng"),
                issue.get("acknowledged_at"),
                issue.get("address", ""),
                issue.get("closed_at"),
                issue.get("comment_url", ""),
                issue.get("comment_count", 0),
                issue.get("html_url", ""),
                json.dumps(issue.get("rating", ""), ensure_ascii=False),
                issue.get("shortened_url", ""),
                issue.get("summary", ""),
                issue.get("url", ""),
                issue.get("vote_count", 0),
                assignee.get("id"),
                assignee.get("name", ""),
                assignee.get("role", ""),
                reporter.get("id"),
                reporter.get("name", ""),
                reporter.get("role", ""),
                request_type.get("id"),
                request_type.get("title", ""),
                request_type.get("organization", "")
            )
            formatted_query = cursor.mogrify(insert_query, values)
            logging.info(f"Formatted SQL Query: {formatted_query}")
            cursor.execute(formatted_query)
        except Exception as e:
            logging.error(f"Error inserting issue {issue.get('id')}: {e}")
            logging.error(f"Offending values: {values}")
    
    conn.commit()
    cursor.close()
    conn.close()
    logging.info(f"Stored {len(issues)} issues into database.")

# Define Airflow DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "seeclickfix_tacoma_dag",
    default_args=default_args,
    description="Fetch and store SeeClickFix data for Tacoma",
    schedule_interval=timedelta(hours=1),
    catchup=False,
)

fetch_task = PythonOperator(
    task_id="fetch_data",
    python_callable=fetch_data,
    provide_context=True,
    dag=dag,
)

store_task = PythonOperator(
    task_id="store_data",
    python_callable=store_data,
    provide_context=True,
    dag=dag,
)

fetch_task >> store_task
