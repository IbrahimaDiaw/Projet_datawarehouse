-- JUNK DIMENSION : regroupe le statut de commande et les drapeaux associes
-- dans une petite dimension (8 lignes) plutot que de laisser des attributs
-- de faible cardinalite dans la table de faits. Notion vue au chapitre 3.
with statuts as (

    select distinct order_status from {{ ref('stg_orders') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['order_status']) }} as status_key,
    order_status                                             as statut_code,
    case order_status
        when 'delivered'    then 'Livree'
        when 'shipped'      then 'Expediee'
        when 'canceled'     then 'Annulee'
        when 'unavailable'  then 'Indisponible'
        when 'invoiced'     then 'Facturee'
        when 'processing'   then 'En traitement'
        when 'created'      then 'Creee'
        when 'approved'     then 'Approuvee'
        else initcap(order_status)
    end                                                      as statut,
    (order_status = 'delivered')                             as is_livree,
    (order_status = 'canceled')                              as is_annulee,
    (order_status in ('delivered', 'shipped', 'invoiced'))   as is_chiffre_affaires,
    case
        when order_status in ('delivered')                          then 'Terminee'
        when order_status in ('canceled', 'unavailable')            then 'Echouee'
        else                                                             'En cours'
    end                                                      as famille_statut
from statuts
