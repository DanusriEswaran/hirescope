"""Quick profile of the Bronze table (read-only)."""
from pathlib import Path

from pyspark.sql import SparkSession, functions as F

ROOT = Path(__file__).resolve().parents[1]
spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")
df = spark.read.parquet(str(ROOT / "data" / "bronze" / "job_postings"))

total = df.count()
print("rows:", total)
print("distinct job_id:", df.select("job_id").distinct().count())
print("salary_min_lpa == 0.0 :", df.filter(F.col("salary_min_lpa").cast("double") == 0).count())
print("salary_disclosed values:")
df.groupBy("salary_disclosed").count().show()
print("skills_required == 'Not Available':", df.filter(F.col("skills_required") == "Not Available").count())
print("duplicates (title+company+primary_city):",
      total - df.select("job_title", "company_name", "primary_city").distinct().count())
for c in ["role_category", "work_mode", "company_size_bucket", "experience_tier"]:
    print(f"--- {c}")
    df.groupBy(c).count().orderBy(F.desc("count")).show(10, truncate=False)
print("--- distinct primary_city:", df.select("primary_city").distinct().count())
df.groupBy("primary_city").count().orderBy(F.desc("count")).show(15, truncate=False)
print("--- sample skills_required")
df.select("skills_required").show(5, truncate=80)
spark.stop()
