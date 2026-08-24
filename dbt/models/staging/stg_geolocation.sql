-- Table volumineuse (~1 000 000 lignes) et fortement redondante : plusieurs
-- points GPS par prefixe de code postal. La deduplication est realisee dans
-- int_geolocation_dedup, AVANT toute jointure avec les dimensions.
with source as (

    select * from {{ source('raw', 'geolocation') }}

),

typed as (

    select
        nullif(trim(geolocation_zip_code_prefix), '')::int   as zip_code_prefix,
        nullif(trim(geolocation_lat), '')::numeric(12, 6)    as latitude,
        nullif(trim(geolocation_lng), '')::numeric(12, 6)    as longitude,
        initcap(trim(geolocation_city))                      as city,
        upper(trim(geolocation_state))                       as state
    from source
    where geolocation_zip_code_prefix is not null

)

select * from typed
-- Bornes geographiques du Bresil : ecarte les coordonnees aberrantes
where latitude between -34.0 and 5.3
  and longitude between -74.0 and -34.7
