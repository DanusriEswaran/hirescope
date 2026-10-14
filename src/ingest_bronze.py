"""Bronze layer: raw CSV -> Parquet (all columns as strings) + load metadata."""
import csv
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession, functions as F

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "indian_tech_jobs.csv"
BRONZE_DIR = ROOT / "data" / "bronze"
TABLE_DIR = BRONZE_DIR / "job_postings"
META_FILE = BRONZE_DIR / "_load_metadata.json"

EXPECTED_COLUMNS = [
    "job_id", "job_title", "company_name", "company_rating", "location",
    "scraped_city", "role_category", "experience_raw", "experience_min_yrs",
    "experience_max_yrs", "salary_raw", "salary_min_lpa", "salary_max_lpa",
    "salary_disclosed", "skills_required", "skills_count", "job_description",
    "posted_date_raw", "work_mode", "company_size_bucket", "job_url",
    "data_source", "scraped_at", "salary_tier", "experience_tier", "is_senior",
    "primary_city", "skill_domain", "salary_midpoint_lpa", "days_since_posted",
    "is_fresher_friendly", "salary_negotiable",
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if not SOURCE.exists():
        sys.exit(f"Source file not found: {SOURCE}")

    spark = (
        SparkSession.builder.master("local[2]")
        .appName("hirescope_bronze")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    # No inferSchema -> every column is read as string (true raw layer).
    df = (
        spark.read.option("header", True)
        .option("multiLine", True)
        .option("quote", '"')
        .option("escape", '"')
        .option("encoding", "UTF-8")
        .csv(str(SOURCE))
    )

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if missing:
        sys.exit(f"Missing columns in CSV: {missing}")
    if extra:
        print(f"Note: extra columns kept as-is: {extra}")

    # Load metadata columns added to every row.
    batch_id = str(uuid.uuid4())
    ingested_at = datetime.now(timezone.utc).isoformat()
    checksum = sha256_of(SOURCE)

    df = (
        df.withColumn("_batch_id", F.lit(batch_id))
        .withColumn("_source_file", F.lit(SOURCE.name))
        .withColumn("_source_sha256", F.lit(checksum))
        .withColumn("_ingested_at", F.lit(ingested_at))
    )

    df.coalesce(1).write.mode("overwrite").parquet(str(TABLE_DIR))

    # Reconcile: CSV record count (Python csv module) vs rows read back from Parquet.
    with open(SOURCE, newline="", encoding="utf-8") as f:
        csv_rows = sum(1 for _ in csv.DictReader(f))
    bronze_rows = spark.read.parquet(str(TABLE_DIR)).count()
    if csv_rows != bronze_rows:
        sys.exit(f"Row mismatch: csv={csv_rows} bronze={bronze_rows}")

    metadata = {
        "batch_id": batch_id,
        "source_file": SOURCE.name,
        "source_sha256": checksum,
        "ingested_at_utc": ingested_at,
        "row_count": bronze_rows,
        "column_count": len(df.columns),
        "output_path": str(TABLE_DIR.relative_to(ROOT)),
    }
    META_FILE.write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2))
    print("Bronze load OK")
    spark.stop()


if __name__ == "__main__":
    main()
