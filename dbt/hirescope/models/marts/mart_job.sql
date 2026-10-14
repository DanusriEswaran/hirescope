-- One row per job with all dimension attributes (dashboard-ready).
select
    f.job_id,
    f.job_title,
    c.company_name,
    r.role_name as role_category,
    l.city,
    f.work_mode,
    f.company_size_bucket,
    f.experience_level,
    f.experience_level_order,
    f.salary_min_lpa,
    f.salary_max_lpa,
    f.salary_mid_lpa,
    f.salary_disclosed,
    f.skills_count
from {{ ref('fact_job_posting') }} f
left join {{ ref('dim_role') }} r on r.role_key = f.role_key
left join {{ ref('dim_location') }} l on l.location_key = f.location_key
left join {{ ref('dim_company') }} c on c.company_key = f.company_key
