FROM apache/airflow:2.7.3-python3.8

USER root
RUN pip install --no-cache-dir psycopg2-binary

USER airflow
WORKDIR /opt/airflow
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
