-- =========================================================================
-- QUESTION METIER 2
-- Quelles categories concentrent le chiffre affaires ?
-- La loi de Pareto (80/20) se verifie-t-elle sur le catalogue Olist ?
-- =========================================================================
with ca_categorie as (

    select
        p.segment,
        p.categorie,
        sum(f.montant_produit)                          as ca_produit,
        sum(f.frais_port)                               as ca_transport,
        sum(f.montant_total)                            as ca_total,
        count(*)                                        as nb_articles,
        count(distinct f.order_id)                      as nb_commandes,
        round(avg(f.montant_produit), 2)                as prix_moyen,
        round(100.0 * sum(f.frais_port) / nullif(sum(f.montant_total), 0), 1)
                                                        as poids_transport_pct
    from marts.fct_order_item f
    inner join marts.dim_product p       on p.product_key = f.product_key
    inner join marts.dim_date d          on d.date_key = f.order_date_key
    inner join marts.dim_order_status s  on s.status_key = f.status_key
    where d.is_periode_analyse
      and s.is_chiffre_affaires
    group by p.segment, p.categorie

),

classement as (

    select
        *,
        row_number() over (order by ca_total desc)                      as rang,
        sum(ca_total) over ()                                           as ca_global,
        sum(ca_total) over (order by ca_total desc
                            rows between unbounded preceding and current row) as ca_cumule
    from ca_categorie

)

select
    rang,
    segment,
    categorie,
    round(ca_total, 2)                                  as ca,
    nb_articles,
    nb_commandes,
    prix_moyen,
    poids_transport_pct,
    round(100.0 * ca_total / ca_global, 2)              as part_pct,
    round(100.0 * ca_cumule / ca_global, 2)             as part_cumulee_pct,
    case
        when 100.0 * ca_cumule / ca_global <= 80 then 'Coeur de gamme (80 % du CA)'
        else 'Longue traine'
    end                                                 as classe_pareto
from classement
order by rang
