-- Grain : une ligne de paiement. Une commande peut en comporter plusieurs
-- (bon d achat + carte de credit par exemple). C est la raison pour laquelle
-- les paiements forment un fait SEPARE de fct_order_item : les joindre aux
-- articles produirait un produit cartesien et un chiffre d affaires fausse.
with source as (

    select * from {{ source('raw', 'order_payments') }}

),

typed as (

    select
        order_id::text                                      as order_id,
        nullif(trim(payment_sequential), '')::int           as payment_sequential,
        lower(trim(payment_type))                           as payment_type,
        nullif(trim(payment_installments), '')::int         as payment_installments,
        nullif(trim(payment_value), '')::numeric(12, 2)     as payment_value
    from source
    where order_id is not null

)

select * from typed
