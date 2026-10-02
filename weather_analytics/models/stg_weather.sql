{{ config(materialized='table') }}

SELECT 
    date,
    latitude,
    longitude,
    temperature_2m,
    wind_speed_10m
FROM read_parquet('s3://weather-lake/processed/**/*.parquet')