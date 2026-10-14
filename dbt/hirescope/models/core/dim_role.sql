select
    cast(row_number() over (order by role_category) as int) as role_key,
    role_category as role_name
from (
    select distinct role_category
    from {{ ref('stg_jobs') }}
    where role_category is not null
) r
