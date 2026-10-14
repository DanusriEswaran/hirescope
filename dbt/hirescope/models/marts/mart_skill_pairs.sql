-- One row per job and skill pair (non-generic skills with enough postings only).
with eligible as (
    select skill_code
    from {{ ref('mart_job_skill') }}
    where not is_generic
    group by skill_code
    having count(*) >= {{ var('min_skill_postings') }}
),
js as (
    select j.*
    from {{ ref('mart_job_skill') }} j
    join eligible e on e.skill_code = j.skill_code
    where not j.is_generic
)
select
    a.job_id,
    a.role_category,
    a.city,
    a.work_mode,
    a.company_size_bucket,
    a.experience_level,
    a.experience_level_order,
    a.skill_name as skill_a,
    b.skill_name as skill_b
from js a
join js b on a.job_id = b.job_id and a.skill_code < b.skill_code
