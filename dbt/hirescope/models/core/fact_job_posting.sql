select
    j.job_id,
    r.role_key,
    l.location_key,
    c.company_key,
    j.job_title,
    j.experience_level,
    j.experience_level_order,
    j.experience_min_yrs,
    j.experience_max_yrs,
    j.work_mode,
    j.company_size_bucket,
    j.salary_min_lpa,
    j.salary_max_lpa,
    j.salary_mid_lpa,
    j.salary_disclosed,
    j.skill_domain,
    j.skills_count,
    j.job_url
from {{ ref('stg_jobs') }} j
left join {{ ref('dim_role') }} r on r.role_name = j.role_category
left join {{ ref('dim_location') }} l on l.city = j.city
left join {{ ref('dim_company') }} c on c.company_name = j.company_name
