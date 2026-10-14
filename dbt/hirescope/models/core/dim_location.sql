select
    cast(row_number() over (order by city) as int) as location_key,
    city,
    (city = 'Remote') as is_remote
from (
    select distinct city
    from {{ ref('stg_jobs') }}
    where city is not null
) c
