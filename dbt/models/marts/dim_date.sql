-- Dimension temps generee (aucune source : c est un referentiel calendaire).
-- Couvre 2016-01-01 -> 2018-12-31, soit la plage du dataset avec une marge.
-- Cle de substitution intelligible : AAAAMMJJ (ex. 20180314).
{{ config(materialized='table') }}

with date_spine as (

    select generate_series(
        '2016-01-01'::date,
        '2018-12-31'::date,
        '1 day'::interval
    )::date as date_day

),

enriched as (

    select
        to_char(date_day, 'YYYYMMDD')::int          as date_key,
        date_day,
        extract(year from date_day)::int            as annee,
        extract(quarter from date_day)::int         as trimestre,
        extract(month from date_day)::int           as mois,
        extract(day from date_day)::int             as jour,
        extract(isodow from date_day)::int          as jour_semaine,
        extract(week from date_day)::int            as semaine_iso,
        date_trunc('month', date_day)::date         as debut_mois,
        date_trunc('quarter', date_day)::date       as debut_trimestre,
        to_char(date_day, 'YYYY-MM')                as annee_mois,
        to_char(date_day, 'YYYY') || '-T' || extract(quarter from date_day)::text
                                                    as annee_trimestre
    from date_spine

)

select
    date_key,
    date_day,
    annee,
    trimestre,
    mois,
    jour,
    jour_semaine,
    semaine_iso,
    debut_mois,
    debut_trimestre,
    annee_mois,
    annee_trimestre,

    case mois
        when 1 then 'Janvier'   when 2 then 'Fevrier'  when 3 then 'Mars'
        when 4 then 'Avril'     when 5 then 'Mai'      when 6 then 'Juin'
        when 7 then 'Juillet'   when 8 then 'Aout'     when 9 then 'Septembre'
        when 10 then 'Octobre'  when 11 then 'Novembre' else 'Decembre'
    end as nom_mois,

    case jour_semaine
        when 1 then 'Lundi'     when 2 then 'Mardi'    when 3 then 'Mercredi'
        when 4 then 'Jeudi'     when 5 then 'Vendredi' when 6 then 'Samedi'
        else 'Dimanche'
    end as nom_jour,

    (jour_semaine >= 6) as is_weekend,

    -- Periode retenue pour les analyses : 2016 est quasi vide (piege qualite n.5)
    (date_day >= '2017-01-01' and date_day < '2018-09-01') as is_periode_analyse

from enriched
