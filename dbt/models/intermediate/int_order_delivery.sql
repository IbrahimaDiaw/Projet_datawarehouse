-- Calcul des indicateurs logistiques au niveau de la commande.
-- Ces mesures sont ensuite portees par fct_order_item (elles sont constantes
-- pour tous les articles d une meme commande : mesure non additive a manipuler
-- avec avg() et non sum()).
with orders as (

    select * from {{ ref('stg_orders') }}

),

calculated as (

    select
        order_id,
        order_status,
        order_purchase_ts,
        order_approved_ts,
        order_delivered_customer_ts,
        order_estimated_delivery_ts,

        -- delai reel entre l achat et la livraison
        case
            when order_delivered_customer_ts is not null
            then extract(epoch from (order_delivered_customer_ts - order_purchase_ts)) / 86400.0
        end::numeric(10, 2) as delivery_days,

        -- delai promis au client a la commande
        extract(epoch from (order_estimated_delivery_ts - order_purchase_ts)) / 86400.0
            as estimated_days_raw,

        -- ecart : positif = retard, negatif = avance
        case
            when order_delivered_customer_ts is not null
            then extract(epoch from (order_delivered_customer_ts - order_estimated_delivery_ts)) / 86400.0
        end::numeric(10, 2) as delay_days,

        -- delai de validation du paiement
        case
            when order_approved_ts is not null
            then extract(epoch from (order_approved_ts - order_purchase_ts)) / 3600.0
        end::numeric(10, 2) as approval_hours

    from orders

)

select
    order_id,
    order_status,
    order_purchase_ts,
    order_delivered_customer_ts,
    order_estimated_delivery_ts,
    delivery_days,
    estimated_days_raw::numeric(10, 2) as estimated_days,
    delay_days,
    approval_hours,

    -- indicateur de ponctualite (NULL si la commande n est jamais arrivee)
    case
        when delay_days is null then null
        when delay_days > 0 then 1
        else 0
    end as is_late,

    -- tranches de retard : axe d analyse de la question metier n.4
    case
        when delay_days is null                         then 'non livre'
        when delay_days <= -10                          then 'tres en avance'
        when delay_days <= -3                           then 'en avance'
        when delay_days <= 0                            then 'a l heure'
        when delay_days <= 3                            then 'retard leger'
        when delay_days <= 10                           then 'retard moyen'
        else                                                 'retard important'
    end as delay_bucket,

    -- PIEGE QUALITE N.4 : ~2 965 commandes n ont pas de date de livraison.
    -- Elles sont conservees (le volume est un KPI en soi) mais exclues des
    -- moyennes logistiques via ce drapeau.
    (order_delivered_customer_ts is null) as is_delivery_unknown

from calculated
