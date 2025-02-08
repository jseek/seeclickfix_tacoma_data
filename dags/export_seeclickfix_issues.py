from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import json
import pandas as pd
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
OUTPUT_FILE_PATH = "/opt/airflow/exports/seeclickfix_issues_dump.parquet"
COUNCIL_GEOJSON_PATH = "/opt/airflow/exports/City_Council_Districts.geojson"
EQUITY_GEOJSON_PATH = "/opt/airflow/exports/Equity_Index_2024_(Tacoma).geojson"
POLICE_GEOJSON_PATH = "/opt/airflow/exports/Police_Districts_(Tacoma).geojson"
SHELTER_GEOJSON_PATH = "/opt/airflow/exports/Estimated10BlockDistancefromShelterView_-7990954508892049150.geojson"

def load_geojson(file_path, attribute_mapping):
    """Load a GeoJSON file and parse polygons with associated attributes."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    features = []
    for feature in data["features"]:
        feature_data = {"geometry": shape(feature["geometry"])}
        feature_data.update({key: feature["properties"].get(value) for key, value in attribute_mapping.items()})
        features.append(feature_data)
    
    return features

def assign_attributes(issue, features, attribute_keys):
    """Assign attributes from the closest matching feature based on lat/lng."""
    point = Point(issue["lng"], issue["lat"])
    for feature in features:
        if feature["geometry"].contains(point):
            for key in attribute_keys:
                issue[key] = feature.get(key, None)
            break  # Stop searching once a match is found

def assign_shelter_proximity(issue, shelters):
    """Assign nearby shelter name and mark if within 10 blocks of any shelter."""
    point = Point(issue["lng"], issue["lat"])
    for shelter in shelters:
        if shelter["geometry"].contains(point):
            issue["nearby_shelter_name"] = shelter.get("shelter_name", "Unknown")
            issue["within_10_blocks_of_shelter"] = True
            return
    issue["nearby_shelter_name"] = None
    issue["within_10_blocks_of_shelter"] = False

def export_to_parquet():
    """Fetch all records from seeclickfix_issues, enrich with spatial data, and save as Parquet."""
    # Connect to the database
    conn = psycopg2.connect(**DB_CONN_PARAMS)
    cursor = conn.cursor()

    query = "SELECT * FROM seeclickfix_issues ORDER BY id"
    cursor.execute(query)
    
    columns = [desc[0] for desc in cursor.description]
    records = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()

    # Load geojson data
    council_districts = load_geojson(COUNCIL_GEOJSON_PATH, {
        "councilmember": "councilmember",
        "councilmember_email": "councilmember_email",
        "councilmember_photo": "councilmember_photo",
        "council_district": "dist_id",
        "councilmember_phonenumber": "phonenumber",
        "councilmember_supportstaff": "supportstaff",
        "councilmember_supportstaff_email": "supportstaff_email",
        "councilmember_webpage": "webpage",
    })

    equity_index = load_geojson(EQUITY_GEOJSON_PATH, {
        "equityindex": "equityindex",
        "livabilityindex": "livabilityindex",
        "accessibilityindex": "accessibilityindex",
        "economicindex": "economicindex",
        "educationindex": "educationindex",
        "environmentalindex": "environmentalindex",
        "averagepavementcondition": "averagepavementcondition",
        "householdvehicleaccess": "householdvehicleaccess",
        "parksopenspace": "parksopenspace",
        "equity_objectid": "objectid",  # Added object_id
    })
    
    police_districts = load_geojson(POLICE_GEOJSON_PATH, {
        "police_sector": "sector",
        "police_district": "district"
    })

    shelters = load_geojson(SHELTER_GEOJSON_PATH, {
        "shelter_name": "Shelter_Name"
    })
    
    # Assign attributes
    for issue in records:
        if "lat" in issue and "lng" in issue:
            assign_attributes(issue, council_districts, [
                "councilmember", "councilmember_email", "councilmember_photo", "council_district",
                "councilmember_phonenumber", "councilmember_supportstaff", "councilmember_supportstaff_email",
                "councilmember_webpage"
            ])
            assign_attributes(issue, equity_index, [
                "equityindex", "livabilityindex", "accessibilityindex", "economicindex", "educationindex",
                "environmentalindex", "averagepavementcondition", "householdvehicleaccess", "parksopenspace",
                "equity_objectid"
            ])
            assign_attributes(issue, police_districts, ["police_sector", "police_district"])
            assign_shelter_proximity(issue, shelters)

    # Convert to DataFrame and save as Parquet
    df = pd.DataFrame(records)
    df.to_parquet(OUTPUT_FILE_PATH, engine='pyarrow', index=False)

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
    description="Export seeclickfix_issues table to Parquet after enriching with council, equity index, police district, and shelter proximity data.",
    schedule_interval="@hourly",
    catchup=False,
)

export_task = PythonOperator(
    task_id="export_to_parquet",
    python_callable=export_to_parquet,
    dag=dag,
)

export_task
