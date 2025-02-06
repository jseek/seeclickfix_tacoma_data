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
PER_PAGE = 20  
SLEEP_SECONDS = 60 / 20  

DEFAULT_UPDATED_AT = "2010-01-01T00:00:00Z"
CREATED_AT_AFTER = "2023-01-01T00:00:00Z"

def get_updated_at():
    """Retrieve last updated timestamp from Airflow Variables."""
    return Variable.get("seeclickfix_last_updated", DEFAULT_UPDATED_AT)

def store_issues(issues):
    """Store issues in the database and update latest updated_at timestamp."""
    if not issues:
        return None
    
    conn = psycopg2.connect(**DB_CONN_PARAMS)
    cursor = conn.cursor()

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
    
    latest_updated_at = None
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
            cursor.execute(insert_query, values)
            
            issue_updated_at = datetime.fromisoformat(issue["updated_at"].replace("Z", "+00:00"))
            if latest_updated_at is None or issue_updated_at > latest_updated_at:
                latest_updated_at = issue_updated_at

        except Exception as e:
            logging.error(f"Error inserting issue {issue.get('id')}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    return latest_updated_at

def fetch_data(**kwargs):
    """Fetch data from SeeClickFix API with pagination and filtering."""
    updated_at = get_updated_at()
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    page = 1
    while True:
        url = f"{BASE_URL}?place_url={PLACE_URL}&details=true&status=archived,open,acknowledged,closed&after={CREATED_AT_AFTER}&sort=updated_at&sort_direction=ASC&per_page={PER_PAGE}&updated_at_after={updated_at}"
        logging.info(f"[PAGE {page}] Fetching data from: {url}")

        start_time = time.time()
        response = session.get(url)
        elapsed_time = time.time() - start_time
        
        if response.status_code != 200:
            logging.error(f"[PAGE {page}] API error {response.status_code}: {response.text}")
            break

        data = response.json()
        issue_count = len(data.get("issues", []))
        total_count = data.get("metadata", {}).get("pagination", {}).get("entries", 0)
        remaining_rate_limit = response.headers.get("X-RateLimit-Remaining", "Unknown")
        
        logging.info(
            f"[PAGE {page}] Received {issue_count} issues | "
            f"Total Count: {total_count} | "
            f"Rate Limit Remaining: {remaining_rate_limit} | "
            f"Request Time: {elapsed_time:.2f} sec"
        )

        if issue_count > 0:
            latest_updated_at = store_issues(data["issues"])
            if latest_updated_at:
                updated_at = latest_updated_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                Variable.set("seeclickfix_last_updated", updated_at)
                logging.info(f"[PAGE {page}] Updated timestamp to: {updated_at}")
        else:
            logging.info(f"[PAGE {page}] No more issues found. Stopping pagination.")
            break

        page += 1
        time.sleep(SLEEP_SECONDS)  # Respect rate limits

# Define Airflow DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "seeclickfix_tacoma_dag",
    default_args=default_args,
    description="Fetch and store SeeClickFix data for Tacoma",
    schedule_interval=timedelta(hours=6),
    catchup=False,
)

fetch_task = PythonOperator(task_id="fetch_data", python_callable=fetch_data, provide_context=True, dag=dag)

fetch_task
