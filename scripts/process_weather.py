import io
import json
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# S3 / SeaweedFS configuration
S3_ENDPOINT = 'http://s3:8333'
AWS_ACCESS_KEY_ID = 'any_key_local'
AWS_SECRET_ACCESS_KEY = 'any_secret_local'
BUCKET_NAME = 'weather-lake'


def clean_and_transform_weather(**kwargs):
  # Setup connection to storage
  s3_client = boto3.client(
      's3',
      endpoint_url=S3_ENDPOINT,
      aws_access_key_id=AWS_ACCESS_KEY_ID,
      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
      region_name='us-east-1',
  )

  execution_date = kwargs['ds']  # YYYY-MM-DD
  raw_key = f'raw/{execution_date}/data.json'

  print(f'Downloading raw data from {raw_key}...')
  obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=raw_key)
  raw_data = obj['Body'].read().decode('utf-8')

  data = json.loads(raw_data)

  # Extract current weather details into a clean table structure
  current = data.get('current', {})
  df = pd.DataFrame([{
      'date': execution_date,
      'latitude': data.get('latitude'),
      'longitude': data.get('longitude'),
      'temperature_2m': current.get('temperature_2m'),
      'wind_speed_10m': current.get('wind_speed_10m'),
  }])

  # Convert DataFrame to Parquet format in memory
  table = pa.Table.from_pandas(df)
  parquet_buffer = io.BytesIO()
  pq.write_table(table, parquet_buffer)

  # Save processed Parquet file back to storage under a 'processed/' folder
  processed_key = f'processed/date={execution_date}/weather.parquet'
  s3_client.put_object(
      Bucket=BUCKET_NAME,
      Key=processed_key,
      Body=parquet_buffer.getvalue(),
      ContentType='application/octet-stream',
  )
  print(
      'Successfully wrote processed parquet data to s3://'
      f'{BUCKET_NAME}/{processed_key}'
  )