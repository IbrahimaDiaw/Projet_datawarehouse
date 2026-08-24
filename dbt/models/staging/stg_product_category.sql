with source as (

    select * from {{ source('raw', 'product_category_translation') }}

)

select
    trim(product_category_name)         as product_category_name,
    trim(product_category_name_english) as product_category_name_en
from source
where product_category_name is not null
