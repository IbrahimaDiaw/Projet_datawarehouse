-- PIEGE QUALITE N.2 : la table geolocation contient environ 1 000 000 de lignes
-- pour seulement ~19 000 prefixes postaux distincts. Une jointure directe
-- multiplierait les lignes de faits et gonflerait le chiffre d affaires.
-- Solution : reduire a un point moyen par prefixe AVANT toute jointure.
with source as (

    select * from {{ ref('stg_geolocation') }}

),

aggregated as (

    select
        zip_code_prefix,
        avg(latitude)::numeric(12, 6)   as latitude,
        avg(longitude)::numeric(12, 6)  as longitude,
        count(*)                        as nb_points_source,
        mode() within group (order by city)  as city,
        mode() within group (order by state) as state
    from source
    group by zip_code_prefix

)

select * from aggregated
