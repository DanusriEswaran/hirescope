# Data dictionary

## Cleaning rules (Silver)

| Field | Rule |
|---|---|
| Duplicates | Same lower-cased title + company + cleaned city; the richest row is kept (valid salary first, then most skills) |
| Salary | `salary_min_lpa`, `salary_max_lpa` kept only if the source flag is true, min >= 1 LPA and max >= min; otherwise null. `salary_mid_lpa` = (min + max) / 2 |
| City | Brackets removed, spaces collapsed, alias list applied (Bangalore to Bengaluru, Gurgaon to Gurugram, Mumbai Suburban to Mumbai and so on) |
| Skills | Split on comma, lowercased, trimmed, alias list applied, junk tags removed, names over 40 characters dropped, one row per job-skill |
| Generic skills | A fixed list of non-specific tags is flagged `is_generic = true` |
| Dropped | `company_rating`, `days_since_posted` (imputed), `job_description` |

## Core tables

| Table | Grain | Key |
|---|---|---|
| `fact_job_posting` | one row per job posting | `job_id` |
| `dim_role` | one row per role category | `role_key` |
| `dim_location` | one row per cleaned city | `location_key` |
| `dim_company` | one row per company name | `company_key` |
| `dim_skill` | one row per normalised skill | `skill_key` |
| `bridge_job_skill` | one row per job and skill | `job_id`, `skill_key` |

## Marts

### mart_job (one row per job)
| Column | Description |
|---|---|
| job_id | Source job id |
| job_title, company_name | As scraped (trimmed) |
| role_category | One of 6 role categories |
| city | Cleaned city; "Remote" is kept as a pseudo-city |
| work_mode | On-site, Hybrid or Remote |
| company_size_bucket | Source size bucket |
| experience_level / experience_level_order | Fresher, Junior, Mid, Senior, Lead/Architect, and sort order 0 to 4 |
| salary_min_lpa, salary_max_lpa, salary_mid_lpa | Null unless the salary is disclosed and valid |
| salary_disclosed | True when the salary is valid |
| skills_count | Number of cleaned skills |

### mart_job_skill (one row per job and skill)
Same filter columns as `mart_job` plus `skill_code`, `skill_name`, `is_generic`. Jobs with no skills get one "(none listed)" row (generic) so job counts stay complete.

### mart_skill_pairs (one row per job and skill pair)
`skill_a`, `skill_b` (non-generic skills with at least 50 postings), plus the same filter columns.
