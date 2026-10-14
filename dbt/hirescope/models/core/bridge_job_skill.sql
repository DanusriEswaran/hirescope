select
    s.job_id,
    d.skill_key
from {{ ref('stg_job_skills') }} s
join {{ ref('dim_skill') }} d on d.skill_code = s.skill_code
