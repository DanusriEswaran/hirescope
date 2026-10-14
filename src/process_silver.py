"""Silver layer: Bronze Parquet -> cleaned `jobs` and `job_skills` Parquet."""
import sys
from pathlib import Path

from pyspark.sql import SparkSession, Window, functions as F

from aliases import CITY_ALIASES, SKILL_ALIASES, SKILL_DISPLAY, SKILL_STOPLIST

ROOT = Path(__file__).resolve().parents[1]
BRONZE = ROOT / "data" / "bronze" / "job_postings"
SILVER = ROOT / "data" / "silver"


def to_map(d):
    return F.create_map(*[F.lit(x) for kv in d.items() for x in kv])


def main():
    if not BRONZE.exists():
        sys.exit("Bronze not found. Run src/ingest_bronze.py first.")

    spark = (
        SparkSession.builder.master("local[2]")
        .appName("hirescope_silver")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    raw = spark.read.parquet(str(BRONZE))
    n_bronze = raw.count()
    n_cities_raw = raw.select("primary_city").distinct().count()

    # ---- cities: strip brackets, collapse spaces, apply alias list
    city_key = F.lower(F.trim(F.regexp_replace(
        F.regexp_replace(F.col("primary_city"), r"\(.*?\)", ""), r"\s+", " ")))
    df = raw.withColumn("city_key", city_key)
    df = df.withColumn(
        "city_clean",
        F.coalesce(to_map(CITY_ALIASES)[F.col("city_key")], F.initcap(F.col("city_key"))),
    )
    df = df.withColumn(
        "city_clean",
        F.when(F.col("city_clean").isNull() | (F.col("city_clean") == ""), F.lit("Unknown"))
        .otherwise(F.col("city_clean")),
    )

    # ---- salary: valid only if flagged disclosed AND min > 0 AND max >= min
    sal_min = F.col("salary_min_lpa").cast("double")
    sal_max = F.col("salary_max_lpa").cast("double")
    flag = F.lower(F.trim(F.col("salary_disclosed"))) == "true"
    valid = F.coalesce(flag & (sal_min > 0) & (sal_max >= sal_min), F.lit(False))
    df = df.withColumn("salary_valid", valid).withColumn("flag_true", F.coalesce(flag, F.lit(False)))
    df = df.withColumn("skills_n_raw", F.col("skills_count").cast("int"))

    # ---- dedupe on title + company + city; keep the richest row
    w = Window.partitionBy(
        F.coalesce(F.lower(F.trim("job_title")), F.col("job_id")),
        F.coalesce(F.lower(F.trim("company_name")), F.lit("")),
        F.col("city_clean"),
    ).orderBy(
        F.col("salary_valid").desc(),
        F.col("skills_n_raw").desc_nulls_last(),
        F.col("job_id").asc(),
    )
    deduped = df.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).cache()
    n_dedup = deduped.count()
    n_flag_true = deduped.filter("flag_true").count()

    # ---- skills: one row per job-skill
    skills = (
        deduped.select("job_id", F.explode(F.split(F.col("skills_required"), ",")).alias("raw"))
        .withColumn("k", F.lower(F.regexp_replace(F.trim(F.col("raw")), r"\s+", " ")))
        .withColumn("k", F.regexp_replace("k", r"^[\s'\";:\-]+|[\s'\";:.\-]+$", ""))
        .filter((F.length("k") > 0) & (F.length("k") <= 40))
        .filter(~F.col("k").isin(list(SKILL_STOPLIST)))
        .withColumn("skill_key", F.coalesce(to_map(SKILL_ALIASES)[F.col("k")], F.col("k")))
        .withColumn(
            "skill_name",
            F.coalesce(
                to_map(SKILL_DISPLAY)[F.col("skill_key")],
                F.concat(F.upper(F.substring("skill_key", 1, 1)), F.substring("skill_key", 2, 100)),
            ),
        )
        .select("job_id", "skill_key", "skill_name")
        .distinct()
    )
    skill_counts = skills.groupBy("job_id").agg(F.count("*").cast("int").alias("skills_count"))

    # ---- jobs: one row per job
    level_order = (
        F.when(F.col("experience_tier").startswith("Fresher"), 0)
        .when(F.col("experience_tier").startswith("Junior"), 1)
        .when(F.col("experience_tier").startswith("Mid"), 2)
        .when(F.col("experience_tier").startswith("Senior"), 3)
        .when(F.col("experience_tier").startswith("Lead"), 4)
    )
    jobs = (
        deduped.select(
            "job_id",
            F.trim("job_title").alias("job_title"),
            F.trim("company_name").alias("company_name"),
            F.trim("role_category").alias("role_category"),
            F.col("city_clean").alias("city"),
            F.trim("work_mode").alias("work_mode"),
            F.trim("company_size_bucket").alias("company_size_bucket"),
            F.trim("experience_tier").alias("experience_level"),
            level_order.alias("experience_level_order"),
            F.col("experience_min_yrs").cast("double").alias("experience_min_yrs"),
            F.col("experience_max_yrs").cast("double").alias("experience_max_yrs"),
            F.when(F.col("salary_valid"), sal_min).alias("salary_min_lpa"),
            F.when(F.col("salary_valid"), sal_max).alias("salary_max_lpa"),
            F.when(F.col("salary_valid"), (sal_min + sal_max) / 2).alias("salary_mid_lpa"),
            F.col("salary_valid").alias("salary_disclosed"),
            F.trim("skill_domain").alias("skill_domain"),
            "job_url",
            "scraped_at",
            "_batch_id",
        )
        .join(skill_counts, "job_id", "left")
        .withColumn("skills_count", F.coalesce(F.col("skills_count"), F.lit(0)))
    )

    jobs.coalesce(1).write.mode("overwrite").parquet(str(SILVER / "jobs"))
    skills.coalesce(1).write.mode("overwrite").parquet(str(SILVER / "job_skills"))

    # ---- summary (read back from disk)
    j = spark.read.parquet(str(SILVER / "jobs"))
    s = spark.read.parquet(str(SILVER / "job_skills"))
    print("\n===== SILVER SUMMARY =====")
    print("bronze rows:", n_bronze)
    print("silver jobs:", j.count(), f"(removed {n_bronze - n_dedup} duplicates)")
    print("job_skills rows:", s.count(), "| distinct skills:", s.select("skill_key").distinct().count())
    print("jobs with 0 skills:", j.filter("skills_count = 0").count())
    print("salary flagged disclosed in source:", n_flag_true,
          "| valid after checks:", j.filter("salary_disclosed").count())
    j.filter("salary_disclosed").agg(
        F.min("salary_min_lpa").alias("min_lpa"),
        F.percentile_approx("salary_mid_lpa", 0.5).alias("median_mid_lpa"),
        F.max("salary_max_lpa").alias("max_lpa"),
    ).show()
    print("distinct cities: raw", n_cities_raw, "-> clean", j.select("city").distinct().count())
    print("cities with < 5 jobs:", j.groupBy("city").count().filter("count < 5").count())
    print("--- top 30 cities")
    j.groupBy("city").count().orderBy(F.desc("count")).show(30, truncate=False)
    print("--- top 40 skills")
    s.groupBy("skill_name").count().orderBy(F.desc("count")).show(40, truncate=False)
    print("--- sample jobs")
    j.select("job_id", "job_title", "city", "experience_level", "salary_mid_lpa", "skills_count").show(5, truncate=40)
    spark.stop()


if __name__ == "__main__":
    main()
