from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'weather_lake_pipeline',
    start_date=datetime(2026, 10, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Task 1 & 2: Your existing ingestion and JSON-to-Parquet tasks...
    # run_ingestion = ...
    # convert_to_parquet = ...

    # Task 3: Run dbt transformations against SeaweedFS via DuckDB
    run_dbt = BashOperator(
        task_id='run_dbt_models',
        bash_command='cd /path/to/weather_analytics && dbt run --profiles-dir .',
    )

    # Task 4: Run dbt quality tests to catch bad data
    test_dbt = BashOperator(
        task_id='test_dbt_models',
        bash_command='cd /path/to/weather_analytics && dbt test --profiles-dir .',
    )

    # Set the pipeline order
    # run_ingestion >> convert_to_parquet >> run_dbt >> test_dbt