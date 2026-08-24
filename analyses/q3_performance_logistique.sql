-- =========================================================================
-- QUESTION METIER 3
-- Quel est le delai moyen de livraison par etat et par vendeur, et quel
-- est le taux de commandes livrees en retard par rapport a la promesse ?
-- =========================================================================
select
    c.region                                                        as region_client,
    c.etat                                                          as etat_client,

    count(distinct f.order_id)                                      as nb_commandes,

    -- delais : mesures NON additives -> moyennes, jamais de somme
    round(avg(f.delai_livraison_jours), 1)                          as delai_moyen_jours,
    round(percentile_cont(0.5) within group (order by f.delai_livraison_jours)::numeric, 1)
                                                                    as delai_median_jours,
    round(percentile_cont(0.9) within group (order by f.delai_livraison_jours)::numeric, 1)
                                                                    as delai_p90_jours,
    round(avg(f.delai_estime_jours), 1)                             as delai_promis_jours,
    round(avg(f.ecart_promesse_jours), 1)                           as ecart_moyen_jours,

    -- ponctualite
    round(100.0 * avg(f.is_retard::numeric), 1)                     as taux_retard_pct,

    -- qualite de la donnee : part de commandes sans date de livraison
    round(100.0 * avg(f.is_livraison_inconnue::int::numeric), 1)    as taux_livraison_inconnue_pct

from marts.fct_order_item f
inner join marts.dim_customer c      on c.customer_key = f.customer_key
inner join marts.dim_date d          on d.date_key = f.order_date_key
inner join marts.dim_order_status s  on s.status_key = f.status_key
where d.is_periode_analyse
  and s.is_livree
group by c.region, c.etat
having count(distinct f.order_id) >= 50   -- seuil de significativite statistique
order by delai_moyen_jours desc
