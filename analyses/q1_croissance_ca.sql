-- =========================================================================
-- QUESTION METIER 1
-- Comment evolue le chiffre affaires par mois / trimestre et par region,
-- et quelle est la croissance mois sur mois (MoM) et annee sur annee (YoY) ?
-- =========================================================================
with ca_mensuel as (

    select
        d.annee_mois,
        d.annee,
        d.mois,
        d.trimestre,
        sum(f.montant_total)            as ca,
        count(distinct f.order_id)      as nb_commandes,
        count(distinct f.customer_key)  as nb_clients,
        sum(f.montant_total) / count(distinct f.order_id) as panier_moyen
    from marts.fct_order_item f
    inner join marts.dim_date d          on d.date_key = f.order_date_key
    inner join marts.dim_order_status s  on s.status_key = f.status_key
    where d.is_periode_analyse           -- exclut la periode 2016 non representative
      and s.is_chiffre_affaires          -- exclut les commandes annulees
    group by d.annee_mois, d.annee, d.mois, d.trimestre

)

select
    annee_mois,
    round(ca, 2)                                    as ca,
    nb_commandes,
    nb_clients,
    round(panier_moyen, 2)                          as panier_moyen,

    -- comparaison temporelle : mois precedent
    round(lag(ca) over (order by annee_mois), 2)    as ca_mois_precedent,
    round(
        100.0 * (ca - lag(ca) over (order by annee_mois))
        / nullif(lag(ca) over (order by annee_mois), 0), 1
    )                                               as croissance_mom_pct,

    -- comparaison temporelle : meme mois annee precedente
    round(lag(ca, 12) over (order by annee_mois), 2) as ca_annee_precedente,
    round(
        100.0 * (ca - lag(ca, 12) over (order by annee_mois))
        / nullif(lag(ca, 12) over (order by annee_mois), 0), 1
    )                                               as croissance_yoy_pct,

    -- cumul annuel glissant
    round(sum(ca) over (partition by annee order by annee_mois), 2) as ca_cumule_annee

from ca_mensuel
order by annee_mois
