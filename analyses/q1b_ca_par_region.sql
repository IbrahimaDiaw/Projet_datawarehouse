-- QUESTION METIER 1 (suite) : repartition geographique du chiffre affaires
select
    c.region,
    c.etat,
    d.annee,
    d.trimestre,
    round(sum(f.montant_total), 2)                                  as ca,
    count(distinct f.order_id)                                      as nb_commandes,
    round(sum(f.montant_total) / count(distinct f.order_id), 2)     as panier_moyen,
    round(
        100.0 * sum(f.montant_total)
        / sum(sum(f.montant_total)) over (partition by d.annee, d.trimestre), 2
    )                                                               as part_ca_pct
from marts.fct_order_item f
inner join marts.dim_customer c      on c.customer_key = f.customer_key
inner join marts.dim_date d          on d.date_key = f.order_date_key
inner join marts.dim_order_status s  on s.status_key = f.status_key
where d.is_periode_analyse
  and s.is_chiffre_affaires
group by c.region, c.etat, d.annee, d.trimestre
order by d.annee, d.trimestre, ca desc
