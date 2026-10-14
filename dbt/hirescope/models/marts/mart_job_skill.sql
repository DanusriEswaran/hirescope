-- One row per job-skill with all filter columns (role, city, experience, work mode).
-- Jobs with no skills get one "(none listed)" row (is_generic = true) so job counts stay complete.
with skill_rows as (
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
),
no_skill_rows as (
    select
        m.job_id,
        'none-listed' as skill_code,
        '(none listed)' as skill_name,
        true as is_generic,
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
    from {{ ref('mart_job') }} m
    where not exists (
        select 1 from {{ ref('bridge_job_skill') }} b where b.job_id = m.job_id
    )
)
select * from skill_rows
union all
select * from no_skill_rows
