-- Dimension vendeur, enrichie de la hierarchie geographique Region > Etat > Ville.
with sellers as (

    select * from {{ ref('stg_sellers') }}

),

geo as (

    select * from {{ ref('int_geolocation_dedup') }}

),

states as (

    select * from {{ ref('br_states') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['s.seller_id']) }} as seller_key,
    s.seller_id,
    s.seller_city                       as ville,
    s.seller_state                      as etat_code,
    coalesce(st.state_name, 'Inconnu')  as etat,
    coalesce(st.region, 'Inconnu')      as region,
    s.seller_zip_code_prefix            as code_postal_prefixe,
    g.latitude,
    g.longitude
from sellers s
left join states st on st.state_code = s.seller_state
left join geo g     on g.zip_code_prefix = s.seller_zip_code_prefix
