-- =========================================================================
-- FAIT SECONDAIRE - paiements
--
-- GRAIN : 1 ligne = 1 MOYEN DE PAIEMENT UTILISE SUR UNE COMMANDE
--         (order_id, payment_sequential)
--
-- Grain different de fct_order_item : les deux faits partagent les memes
-- dimensions (constellation de faits) mais ne doivent JAMAIS etre joints
-- directement, sous peine de produit cartesien.
-- =========================================================================
{{ config(materialized='table') }}

with payments as (

    select * from {{ ref('stg_order_payments') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

customers as (

    select customer_id, customer_unique_id from {{ ref('stg_customers') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['p.order_id', 'p.payment_sequential']) }} as payment_key,

    p.order_id,
    p.payment_sequential,

    dd.date_key                     as order_date_key,
    dc.customer_key,
    dos.status_key,

    p.payment_type                  as type_paiement,
    case p.payment_type
        when 'credit_card' then 'Carte de credit'
        when 'boleto'      then 'Boleto (virement)'
        when 'voucher'     then 'Bon achat'
        when 'debit_card'  then 'Carte de debit'
        else 'Non defini'
    end                             as libelle_paiement,

    -- MESURES
    p.payment_value                 as montant_paye,
    p.payment_installments          as nb_echeances,
    case
        when p.payment_installments is null or p.payment_installments <= 1 then 'Comptant'
        when p.payment_installments <= 3                                   then '2-3 fois'
        when p.payment_installments <= 6                                   then '4-6 fois'
        when p.payment_installments <= 12                                  then '7-12 fois'
        else                                                                    'Plus de 12 fois'
    end                             as tranche_echeances

from payments p
inner join orders    o   on o.order_id = p.order_id
inner join customers c   on c.customer_id = o.customer_id
inner join {{ ref('dim_customer') }}     dc  on dc.customer_unique_id = c.customer_unique_id
inner join {{ ref('dim_order_status') }} dos on dos.statut_code = o.order_status
inner join {{ ref('dim_date') }}         dd  on dd.date_key = to_char(o.order_purchase_ts, 'YYYYMMDD')::int
