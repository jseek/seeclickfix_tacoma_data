from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import json
from shapely.geometry import shape, Point

# Database connection parameters
DB_CONN_PARAMS = {
    "dbname": "airflow",
    "user": "airflow",
    "password": "airflow",
    "host": "postgres",
    "port": 5432,
}

# File paths
OUTPUT_FILE_PATH = "/opt/airflow/exports/seeclickfix_issues_dump.json"
GEOJSON_FILE_PATH = "/opt/airflow/exports/City_Council_Districts.geojson"

def load_geojson():
    """Load the City Council Districts geojson file and parse polygons."""
    with open(GEOJSON_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    districts = []
    for feature in data["features"]:
        district = {
            "geometry": shape(feature["geometry"]),  # Convert geometry to a Shapely polygon
            "councilmember": feature["properties"].get("councilmember"),
            "councilmember_email": feature["properties"].get("councilmember_email"),
            "councilmember_photo": feature["properties"].get("councilmember_photo"),
            "council_distinct": feature["properties"].get("dist_id"),
            "councilmember_phonenumber": feature["properties"].get("phonenumber"),
            "councilmember_supportstaff": feature["properties"].get("supportstaff"),
            "councilmember_supportstaff_email": feature["properties"].get("supportstaff_email"),
            "councilmember_webpage": feature["properties"].get("webpage"),
        }
        districts.append(district)
    
    return districts

def assign_council_data(issue, districts):
    """Assign council district data to an issue based on its lat/lng."""
    point = Point(issue["lng"], issue["lat"])  # Create a Shapely Point
    for district in districts:
        if district["geometry"].contains(point):
            issue.update({
                "councilmember": district["councilmember"],
                "councilmember_email": district["councilmember_email"],
                "councilmember_photo": district["councilmember_photo"],
                "councilmember_phonenumber": district["councilmember_phonenumber"],
                "councilmember_supportstaff": district["councilmember_supportstaff"],
                "councilmember_supportstaff_email": district["councilmember_supportstaff_email"],
                "councilmember_webpage": district["councilmember_webpage"],
                "council_distinct": district["council_distinct"],
            })
            break  # Stop searching once a match is found

def export_to_json():
    """Fetch all records from seeclickfix_issues, enrich with council data, and save as JSON."""
    # Connect to the database
    conn = psycopg2.connect(**DB_CONN_PARAMS)
    cursor = conn.cursor()

    query = "SELECT * FROM seeclickfix_issues ORDER BY id"
    cursor.execute(query)
    
    columns = [desc[0] for desc in cursor.description]
    records = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()

    # Load council district polygons
    districts = load_geojson()

    # Assign councilmember data to each issue
    for issue in records:
        if "lat" in issue and "lng" in issue:
            assign_council_data(issue, districts)

    # Save enriched data to JSON
    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False, default=str)

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
    description="Export seeclickfix_issues table to JSON after enriching with council district data.",
    schedule_interval="@hourly",
    catchup=False,
)

export_task = PythonOperator(
    task_id="export_to_json",
    python_callable=export_to_json,
    dag=dag,
)

export_task
