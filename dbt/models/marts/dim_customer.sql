-- Dimension client (SCD de type 1 : le dataset ne fournit aucun historique
-- d adresse, on conserve donc l etat le plus recent connu ; le choix est
-- justifie dans le rapport).
-- PIEGE QUALITE N.1 : la dimension est construite sur customer_unique_id
-- et NON sur customer_id, qui n est qu une cle technique par commande.
with customers as (

    select * from {{ ref('stg_customers') }}

),

orders as (

    select order_id, customer_id, order_purchase_ts from {{ ref('stg_orders') }}

),

joined as (

    select
        c.customer_unique_id,
        c.customer_id,
        c.customer_zip_code_prefix,
        c.customer_city,
        c.customer_state,
        o.order_id,
        o.order_purchase_ts
    from customers c
    left join orders o on o.customer_id = c.customer_id

),

-- attributs les plus recents connus pour chaque client
latest_attributes as (

    select
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        row_number() over (
            partition by customer_unique_id
            order by order_purchase_ts desc nulls last, customer_id
        ) as rn
    from joined

),

-- historique d achat agrege
purchase_history as (

    select
        customer_unique_id,
        count(distinct order_id)    as nb_commandes,
        min(order_purchase_ts)      as premiere_commande_ts,
        max(order_purchase_ts)      as derniere_commande_ts
    from joined
    group by customer_unique_id

),

geo as (

    select * from {{ ref('int_geolocation_dedup') }}

),

states as (

    select * from {{ ref('br_states') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['a.customer_unique_id']) }} as customer_key,
    a.customer_unique_id,
    a.customer_city                                 as ville,
    a.customer_state                                as etat_code,
    coalesce(s.state_name, 'Inconnu')               as etat,
    coalesce(s.region, 'Inconnu')                   as region,
    a.customer_zip_code_prefix                      as code_postal_prefixe,
    g.latitude,
    g.longitude,
    h.nb_commandes,
    h.premiere_commande_ts,
    h.derniere_commande_ts,
    (h.nb_commandes > 1)                            as is_client_recurrent,
    case
        when h.nb_commandes >= 3 then 'Fidele (3+)'
        when h.nb_commandes = 2  then 'Repeteur (2)'
        else 'Unique (1)'
    end                                             as segment_fidelite
from latest_attributes a
left join purchase_history h on h.customer_unique_id = a.customer_unique_id
left join states s           on s.state_code = a.customer_state
left join geo g              on g.zip_code_prefix = a.customer_zip_code_prefix
where a.rn = 1
