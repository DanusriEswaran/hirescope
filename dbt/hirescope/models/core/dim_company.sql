select
    cast(row_number() over (order by company_name) as int) as company_key,
    company_name
from (
    select distinct company_name
    from {{ ref('stg_jobs') }}
    where company_name is not null
) c
