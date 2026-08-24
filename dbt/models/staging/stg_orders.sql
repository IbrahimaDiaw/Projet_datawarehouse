-- Typage des commandes. Les chaines vides du CSV deviennent des NULL.
with source as (

    select * from {{ source('raw', 'orders') }}

),

typed as (

    select
        order_id::text                                              as order_id,
        customer_id::text                                           as customer_id,
        lower(trim(order_status))                                   as order_status,
        nullif(trim(order_purchase_timestamp), '')::timestamp       as order_purchase_ts,
        nullif(trim(order_approved_at), '')::timestamp              as order_approved_ts,
        nullif(trim(order_delivered_carrier_date), '')::timestamp   as order_delivered_carrier_ts,
        nullif(trim(order_delivered_customer_date), '')::timestamp  as order_delivered_customer_ts,
        nullif(trim(order_estimated_delivery_date), '')::timestamp  as order_estimated_delivery_ts
    from source
    where order_id is not null

)

select * from typed
