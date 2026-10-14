select
    cast(row_number() over (order by skill_code) as int) as skill_key,
    skill_code,
    skill_name,
    is_generic
from (
    select
        skill_code,
        max(skill_name) as skill_name,
        bool_or(is_generic) as is_generic
    from {{ ref('stg_job_skills') }}
    group by skill_code
) s
