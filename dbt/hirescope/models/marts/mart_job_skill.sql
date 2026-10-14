-- One row per job-skill with all filter columns (role, city, experience, work mode).
select
    m.job_id,
    d.skill_code,
    d.skill_name,
    d.is_generic,
    m.role_category,
    m.city,
    m.work_mode,
    m.company_size_bucket,
    m.experience_level,
    m.experience_level_order,
    m.salary_min_lpa,
    m.salary_max_lpa,
    m.salary_mid_lpa,
    m.salary_disclosed
from {{ ref('bridge_job_skill') }} b
join {{ ref('dim_skill') }} d on d.skill_key = b.skill_key
join {{ ref('mart_job') }} m on m.job_id = b.job_id
