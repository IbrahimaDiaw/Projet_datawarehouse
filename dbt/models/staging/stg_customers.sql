-- Regle de gestion majeure : customer_id identifie une COMMANDE cote client,
-- customer_unique_id identifie le CLIENT reel. Toute analyse client doit
-- s appuyer sur customer_unique_id, sinon le taux de clients recurrents = 0.
with source as (

    select * from {{ source('raw', 'customers') }}

),

typed as (

    select
        customer_id::text                                   as customer_id,
        customer_unique_id::text                            as customer_unique_id,
        nullif(trim(customer_zip_code_prefix), '')::int     as customer_zip_code_prefix,
        initcap(trim(customer_city))                        as customer_city,
        upper(trim(customer_state))                         as customer_state
    from source
    where customer_id is not null

)

select * from typed
