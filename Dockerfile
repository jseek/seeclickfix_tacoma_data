FROM apache/airflow:latest

USER airflow

RUN pip install --no-cache-dir psycopg2-binary

USER airflow
WORKDIR /opt/airflow
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt