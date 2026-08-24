-- =========================================================================
-- TABLE DE FAITS PRINCIPALE - fait transactionnel
--
-- GRAIN : 1 ligne = 1 ARTICLE D UNE COMMANDE  (order_id, order_item_id)
--         soit ~112 650 lignes.
--
-- C est la declaration de grain la plus importante du projet : toutes les
-- mesures ci-dessous sont exprimees a ce niveau, et aucune ligne ne peut
-- etre dupliquee sans fausser le chiffre d affaires.
-- =========================================================================
{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['order_date_key']},
            {'columns': ['customer_key']},
            {'columns': ['product_key']},
            {'columns': ['seller_key']}
        ]
    )
}}

with items as (

    select * from {{ ref('stg_order_items') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

delivery as (

    select * from {{ ref('int_order_delivery') }}

),

customers as (

    select customer_id, customer_unique_id from {{ ref('stg_customers') }}

)

select
    -- cle de substitution du fait
    {{ dbt_utils.generate_surrogate_key(['i.order_id', 'i.order_item_id']) }} as order_item_key,

    -- DIMENSION DEGENEREE : le numero de commande est conserve dans le fait
    -- (utile pour compter les commandes distinctes et le panier moyen)
    i.order_id,
    i.order_item_id,

    -- cles etrangeres vers les dimensions
    dd.date_key                             as order_date_key,
    dl.date_key                             as delivered_date_key,
    dc.customer_key,
    dp.product_key,
    ds.seller_key,
    dos.status_key,

    -- ---------------- MESURES ADDITIVES ----------------
    i.price                                 as montant_produit,
    i.freight_value                         as frais_port,
    (i.price + i.freight_value)             as montant_total,
    1                                       as quantite,

    -- ---------------- MESURES NON ADDITIVES ------------
    -- (constantes au niveau de la commande : utiliser avg(), jamais sum())
    d.delivery_days                         as delai_livraison_jours,
    d.estimated_days                        as delai_estime_jours,
    d.delay_days                            as ecart_promesse_jours,
    d.approval_hours                        as delai_validation_heures,
    d.is_late                               as is_retard,
    d.delay_bucket                          as tranche_retard,

    -- ---------------- DRAPEAUX QUALITE -----------------
    d.is_delivery_unknown                   as is_livraison_inconnue,
    o.order_purchase_ts                     as date_achat,
    o.order_delivered_customer_ts           as date_livraison

from items i
inner join orders     o   on o.order_id = i.order_id
inner join delivery   d   on d.order_id = i.order_id
inner join customers  c   on c.customer_id = o.customer_id
inner join {{ ref('dim_customer') }}     dc  on dc.customer_unique_id = c.customer_unique_id
inner join {{ ref('dim_product') }}      dp  on dp.product_id = i.product_id
inner join {{ ref('dim_seller') }}       ds  on ds.seller_id = i.seller_id
inner join {{ ref('dim_order_status') }} dos on dos.statut_code = o.order_status
inner join {{ ref('dim_date') }}         dd  on dd.date_key = to_char(o.order_purchase_ts, 'YYYYMMDD')::int
left  join {{ ref('dim_date') }}         dl  on dl.date_key = to_char(o.order_delivered_customer_ts, 'YYYYMMDD')::int
