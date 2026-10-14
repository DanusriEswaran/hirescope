-- Runs once, on first start of an empty volume.
CREATE SCHEMA IF NOT EXISTS raw;
-- Metadata DBs for later phases (Metabase, Airflow), created now to avoid a volume reset later.
CREATE DATABASE metabase;
CREATE DATABASE airflow;
