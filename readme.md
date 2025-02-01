# **SeeClickFix Tacoma Data**

This repo reviews 311 issues from SeeClickFix (SCF) for the City Of Tacoma, pulling the data from the SCF api and loads it to a database, then visualizes it in Streamlit. This dashboard highlights areas of concern in the city, issues that effect different parts of the city disproportionately, and the effectiveness of city offices in dealing with issues.

## **Streamlit Dashboard**
After following the instructions below to get the project running, wait while airflow populates the issues. The Streamlit app provides interactive visualizations for SeeClickFix data, allowing users to analyze reported issues in the city. Features include:

- **Filtering by Date & Summary** – Users can refine issue data by selecting date ranges and specific issue summaries.  
- **Aging Analysis Table** – Displays the median time to acknowledge an issue, count of acknowledged issues, and percentage acknowledged.  
- **Weekly Time Series Chart** – Shows trends of reported issues over time.  
- **Scatter Map of Issues** – A geographical view of reported issues.  
- **Heatmap of Issue Density** – Identifies high-density problem areas.  
- **Bar Chart of Issues by Summary** – Visualizes the most reported issue types.  
- **Pie Chart for Homeless-Related Issues** – Highlights the proportion of reports related to homelessness.  
- **Filterable Table of Issue Data** – Allows users to explore raw data interactively.  
- **Overburdened Areas Analysis** – Groups issues by geographic region to find neighborhoods with high report volumes.  
- **Chronic Areas** – Identifies locations with frequent reports, grouped by quarter-mile.  

To access the dashboard, open [http://localhost:8501](http://localhost:8501) in your browser after issues are loaded to the database. You may need to run `docker restart streamlit` after the issues load.

---

## **Project Overview**  
Package includes:  
- **Apache Airflow** – for getting the issues from SCF  
- **PostgreSQL** – used as Airflow’s metadata database  
- **pgAdmin** – a web-based UI for managing the PostgreSQL database  
- **Streamlit** – an interactive dashboard for visualizing SeeClickFix data  

## **Getting Started**  

### **1. Clone the Repository**  
```sh
git clone https://github.com/jseek/seeclickfix_tacoma_data.git
cd seeclickfix_tacoma_data
```

### **2. Start the Services**  
```sh
docker-compose up -d
```
This will:  
- Start **PostgreSQL** on port `5432`  
- Start **Airflow** (webserver & scheduler) on port `8080`  
- Start **pgAdmin** on port `5059`  
- Start **Streamlit Dashboard** on port `8501`  

### **3. Access the Services**  
| Service       | URL                                  | Credentials |
|--------------|--------------------------------------|------------|
| **Airflow**   | [http://localhost:8080](http://localhost:8080) | `admin` / `admin` | You may need to enable the dag.
| **pgAdmin**   | [http://localhost:5059](http://localhost:5059) | `admin@example.com` / `admin` |
| **Streamlit** | [http://localhost:8501](http://localhost:8501) | N/A |

### **4. Connect pgAdmin to PostgreSQL**  
1. Open **pgAdmin** at [http://localhost:5059](http://localhost:5059).  
2. Login with `admin@example.com` / `admin`.  
3. Click **Add New Server** and enter:  
   - **Host**: `postgres`  
   - **Username**: `airflow`  
   - **Password**: `airflow`  
   - **Database**: `airflow`  
4. Click **Save** to connect.

---

## **Project Structure**  
```
seeclickfix_tacoma_data/
│-- docker-compose.yml     # Defines services (Airflow, Postgres, pgAdmin, Streamlit)
│-- Dockerfile             # Airflow image with PostgreSQL support
│-- requirements.txt       # Python dependencies
│-- dags/                  # Airflow DAGs for fetching & storing data
│-- streamlit_app.py       # Streamlit dashboard application
```

## **Stopping & Cleaning Up**  
To stop the containers:  
```sh
docker-compose down
```
To remove everything (containers, networks, volumes):  
```sh
docker-compose down -v
```