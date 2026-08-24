-- CONTROLE DE VOLUMETRIE  (severite : warn)
-- Detecte les mois anormalement creux, qui rendraient toute comparaison
-- temporelle trompeuse. Sur Olist, ce test remonte septembre-decembre 2016
-- (quelques commandes seulement) : c est ce constat qui justifie de
-- restreindre la periode analysee a 2017-01 -> 2018-08.
{{ config(severity='warn') }}

with volume_mensuel as (

    select
        d.annee_mois,
        count(distinct f.order_id) as nb_commandes
    from {{ ref('fct_order_item') }} f
    inner join {{ ref('dim_date') }} d on d.date_key = f.order_date_key
    group by d.annee_mois

)

select *
from volume_mensuel
where nb_commandes < 100
order by annee_mois
