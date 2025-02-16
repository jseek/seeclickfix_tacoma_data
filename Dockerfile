FROM apache/airflow:latest

USER airflow

RUN pip install --no-cache-dir psycopg2-binary
RUN pip install --no-cache-dir scikit-learn

USER airflow
WORKDIR /opt/airflow
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt