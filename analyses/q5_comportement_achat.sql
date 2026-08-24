-- =========================================================================
-- QUESTION METIER 5
-- Panier moyen, part de clients recurrents, repartition des moyens de
-- paiement et recours au paiement en plusieurs fois.
-- =========================================================================

-- 5.a  Moyens de paiement et echeances
select
    'A. Moyens de paiement'         as bloc,
    p.libelle_paiement              as modalite,
    p.tranche_echeances             as detail,
    count(*)                        as nb_paiements,
    round(sum(p.montant_paye), 2)   as montant_total,
    round(avg(p.montant_paye), 2)   as montant_moyen,
    round(100.0 * sum(p.montant_paye) / sum(sum(p.montant_paye)) over (), 1) as part_pct
from marts.fct_order_payment p
inner join marts.dim_date d on d.date_key = p.order_date_key
where d.is_periode_analyse
group by p.libelle_paiement, p.tranche_echeances

union all

-- 5.b  Fidelite client
select
    'B. Fidelite'                   as bloc,
    c.segment_fidelite              as modalite,
    c.region                        as detail,
    count(distinct c.customer_key)  as nb_paiements,
    round(sum(f.montant_total), 2)  as montant_total,
    round(sum(f.montant_total) / count(distinct f.order_id), 2) as montant_moyen,
    round(100.0 * count(distinct c.customer_key)
          / sum(count(distinct c.customer_key)) over (), 1)     as part_pct
from marts.fct_order_item f
inner join marts.dim_customer c on c.customer_key = f.customer_key
inner join marts.dim_date d     on d.date_key = f.order_date_key
where d.is_periode_analyse
group by c.segment_fidelite, c.region

order by bloc, montant_total desc
