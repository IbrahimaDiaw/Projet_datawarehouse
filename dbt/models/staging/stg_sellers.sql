with source as (

    select * from {{ source('raw', 'sellers') }}

),

typed as (

    select
        seller_id::text                                 as seller_id,
        nullif(trim(seller_zip_code_prefix), '')::int   as seller_zip_code_prefix,
        initcap(trim(seller_city))                      as seller_city,
        upper(trim(seller_state))                       as seller_state
    from source
    where seller_id is not null

)

select * from typed
