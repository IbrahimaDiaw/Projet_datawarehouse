-- Grain : un article d'une commande. Cle naturelle = (order_id, order_item_id).
with source as (

    select * from {{ source('raw', 'order_items') }}

),

typed as (

    select
        order_id::text                                      as order_id,
        order_item_id::int                                  as order_item_id,
        product_id::text                                    as product_id,
        seller_id::text                                     as seller_id,
        nullif(trim(shipping_limit_date), '')::timestamp    as shipping_limit_ts,
        nullif(trim(price), '')::numeric(12, 2)             as price,
        nullif(trim(freight_value), '')::numeric(12, 2)     as freight_value
    from source
    where order_id is not null

)

select * from typed
