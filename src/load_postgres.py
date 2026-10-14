"""Load Silver Parquet into Postgres schema `raw` (idempotent: truncate + reload)."""
import json
import math
import sys
from pathlib import Path

import psycopg2
import pyarrow.parquet as pq
from psycopg2.extras import execute_values

ROOT = Path(__file__).resolve().parents[1]
SILVER = ROOT / "data" / "silver"
BRONZE_META = ROOT / "data" / "bronze" / "_load_metadata.json"

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.jobs (
    job_id                 text PRIMARY KEY,
    job_title              text,
    company_name           text,
    role_category          text,
    city                   text,
    work_mode              text,
    company_size_bucket    text,
    experience_level       text,
    experience_level_order integer,
    experience_min_yrs     double precision,
    experience_max_yrs     double precision,
    salary_min_lpa         numeric(8,2),
    salary_max_lpa         numeric(8,2),
    salary_mid_lpa         numeric(8,2),
    salary_disclosed       boolean,
    skill_domain           text,
    job_url                text,
    scraped_at             text,
    batch_id               text,
    skills_count           integer
);

CREATE TABLE IF NOT EXISTS raw.job_skills (
    job_id      text NOT NULL,
    skill_key   text NOT NULL,
    skill_name  text,
    is_generic  boolean,
    PRIMARY KEY (job_id, skill_key)
);

CREATE TABLE IF NOT EXISTS raw.load_metadata (
    batch_id         text,
    source_file      text,
    source_sha256    text,
    ingested_at_utc  timestamptz,
    bronze_rows      integer,
    silver_jobs      integer,
    silver_job_skills integer,
    loaded_at        timestamptz DEFAULT now()
);
"""

JOBS_SRC = [
    "job_id", "job_title", "company_name", "role_category", "city", "work_mode",
    "company_size_bucket", "experience_level", "experience_level_order",
    "experience_min_yrs", "experience_max_yrs", "salary_min_lpa", "salary_max_lpa",
    "salary_mid_lpa", "salary_disclosed", "skill_domain", "job_url", "scraped_at",
    "_batch_id", "skills_count",
]
JOBS_DST = [c if c != "_batch_id" else "batch_id" for c in JOBS_SRC]
SKILLS_COLS = ["job_id", "skill_key", "skill_name", "is_generic"]


def load_env() -> dict:
    env = {}
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def read_rows(path: Path, cols: list):
    table = pq.read_table(str(path))
    missing = [c for c in cols if c not in table.column_names]
    if missing:
        sys.exit(f"{path.name}: missing columns {missing}. Re-run src/process_silver.py")
    data = [table.column(c).to_pylist() for c in cols]
    rows = [
        tuple(None if isinstance(v, float) and math.isnan(v) else v for v in r)
        for r in zip(*data)
    ]
    return rows


def main() -> None:
    env = load_env()
    conn = psycopg2.connect(
        host="localhost",
        port=int(env.get("POSTGRES_PORT", 5432)),
        dbname=env.get("POSTGRES_DB", "hirescope"),
        user=env.get("POSTGRES_USER", "hirescope"),
        password=env.get("POSTGRES_PASSWORD", "hirescope_pw"),
    )
    jobs = read_rows(SILVER / "jobs", JOBS_SRC)
    skills = read_rows(SILVER / "job_skills", SKILLS_COLS)
    meta = json.loads(BRONZE_META.read_text())

    with conn:  # one transaction: all or nothing
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute("TRUNCATE raw.jobs, raw.job_skills")
            execute_values(
                cur,
                f"INSERT INTO raw.jobs ({', '.join(JOBS_DST)}) VALUES %s",
                jobs, page_size=5000,
            )
            execute_values(
                cur,
                f"INSERT INTO raw.job_skills ({', '.join(SKILLS_COLS)}) VALUES %s",
                skills, page_size=5000,
            )
            cur.execute("SELECT count(*) FROM raw.jobs")
            n_jobs = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM raw.job_skills")
            n_skills = cur.fetchone()[0]
            if n_jobs != len(jobs) or n_skills != len(skills):
                raise RuntimeError(f"Count mismatch: jobs {n_jobs}/{len(jobs)}, skills {n_skills}/{len(skills)}")
            cur.execute(
                """INSERT INTO raw.load_metadata
                   (batch_id, source_file, source_sha256, ingested_at_utc,
                    bronze_rows, silver_jobs, silver_job_skills)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (meta["batch_id"], meta["source_file"], meta["source_sha256"],
                 meta["ingested_at_utc"], meta["row_count"], n_jobs, n_skills),
            )
    conn.close()
    print(f"Loaded raw.jobs: {n_jobs} rows | raw.job_skills: {n_skills} rows")
    print("Postgres load OK")


if __name__ == "__main__":
    main()
