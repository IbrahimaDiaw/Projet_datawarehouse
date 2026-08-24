-- CONTROLE DE COMPLETUDE
-- Le fait principal doit contenir exactement autant de lignes que la source :
-- si une jointure de dimension echoue (inner join), des ventes disparaissent
-- silencieusement du chiffre d affaires. Ce test detecte cette fuite.
with source as (

    select count(*) as nb from {{ ref('stg_order_items') }}

),

fait as (

    select count(*) as nb from {{ ref('fct_order_item') }}

)

select
    source.nb as nb_lignes_source,
    fait.nb   as nb_lignes_fait,
    source.nb - fait.nb as ecart
from source, fait
where source.nb <> fait.nb
