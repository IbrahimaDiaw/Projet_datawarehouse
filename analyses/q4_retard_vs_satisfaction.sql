-- =========================================================================
-- QUESTION METIER 4
-- Quel est impact du retard de livraison sur la satisfaction client ?
-- Croisement du fait satisfaction et des mesures logistiques.
-- =========================================================================
select
    r.tranche_retard,

    count(*)                                                as nb_avis,
    round(100.0 * count(*) / sum(count(*)) over (), 1)      as part_avis_pct,

    round(avg(r.note), 2)                                   as note_moyenne,
    round(100.0 * avg(r.is_satisfait::int::numeric), 1)     as taux_satisfaction_pct,
    round(100.0 * avg(r.is_insatisfait::int::numeric), 1)   as taux_insatisfaction_pct,
    round(avg(r.delai_livraison_jours), 1)                  as delai_moyen_jours,

    -- ecart a la note moyenne globale : mesure directe de impact
    round(avg(r.note) - (select avg(note) from marts.fct_order_review), 2)
                                                            as ecart_note_vs_moyenne

from marts.fct_order_review r
inner join marts.dim_date d on d.date_key = r.order_date_key
where d.is_periode_analyse
group by r.tranche_retard
order by
    case r.tranche_retard
        when 'tres en avance'   then 1
        when 'en avance'        then 2
        when 'a l heure'        then 3
        when 'retard leger'     then 4
        when 'retard moyen'     then 5
        when 'retard important' then 6
        else 7
    end
