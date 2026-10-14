select
    job_id,
    skill_key as skill_code,
    skill_name,
    is_generic
from {{ source('raw', 'job_skills') }}
