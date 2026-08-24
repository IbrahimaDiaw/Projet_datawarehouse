-- =========================================================================
-- CARTES KPI de la page accueil du tableau de bord
-- =========================================================================
select
    round(sum(f.montant_total), 2)                              as ca_total,
    count(distinct f.order_id)                                  as nb_commandes,
    count(distinct f.customer_key)                              as nb_clients,
    round(sum(f.montant_total) / count(distinct f.order_id), 2) as panier_moyen,
    round(avg(f.delai_livraison_jours), 1)                      as delai_moyen_jours,
    round(100.0 * avg(f.is_retard::numeric), 1)                 as taux_retard_pct,
    (select round(avg(note), 2) from marts.fct_order_review)    as note_moyenne,
    (select round(100.0 * avg(is_client_recurrent::int::numeric), 1)
     from marts.dim_customer)                                   as taux_clients_recurrents_pct
from marts.fct_order_item f
inner join marts.dim_date d          on d.date_key = f.order_date_key
inner join marts.dim_order_status s  on s.status_key = f.status_key
where d.is_periode_analyse
  and s.is_chiffre_affaires
