-- =========================================================================
-- FAIT SECONDAIRE - satisfaction client
--
-- GRAIN : 1 ligne = 1 AVIS (une commande notee, apres deduplication).
--
-- Ce fait porte la question metier n.4 : mesurer impact du retard de
-- livraison sur la note attribuee par le client. Il embarque donc la
-- tranche de retard issue de int_order_delivery.
-- =========================================================================
{{ config(materialized='table') }}

with reviews as (

    select * from {{ ref('stg_order_reviews') }}

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
    {{ dbt_utils.generate_surrogate_key(['r.order_id']) }} as review_key,

    r.review_id,
    r.order_id,

    dd.date_key                 as order_date_key,
    dr.date_key                 as review_date_key,
    dc.customer_key,
    dos.status_key,

    -- MESURES
    r.review_score              as note,
    (r.review_score >= 4)       as is_satisfait,
    (r.review_score <= 2)       as is_insatisfait,
    r.has_comment               as is_commente,
    case
        when r.review_answer_ts is not null and r.review_creation_ts is not null
        then (extract(epoch from (r.review_answer_ts - r.review_creation_ts)) / 3600.0)::numeric(10, 2)
    end                         as delai_reponse_heures,

    -- axes analyse repris du fait logistique
    d.delivery_days             as delai_livraison_jours,
    d.delay_days                as ecart_promesse_jours,
    d.delay_bucket              as tranche_retard,
    d.is_late                   as is_retard

from reviews r
inner join orders    o   on o.order_id = r.order_id
inner join delivery  d   on d.order_id = r.order_id
inner join customers c   on c.customer_id = o.customer_id
inner join {{ ref('dim_customer') }}     dc  on dc.customer_unique_id = c.customer_unique_id
inner join {{ ref('dim_order_status') }} dos on dos.statut_code = o.order_status
inner join {{ ref('dim_date') }}         dd  on dd.date_key = to_char(o.order_purchase_ts, 'YYYYMMDD')::int
left  join {{ ref('dim_date') }}         dr  on dr.date_key = to_char(r.review_creation_ts, 'YYYYMMDD')::int
