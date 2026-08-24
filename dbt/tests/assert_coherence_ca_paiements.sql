-- CONTROLE DE COHERENCE INTER-FAITS  (severite : warn)
-- Pour une meme commande, le total facture (fct_order_item) devrait
-- correspondre au total encaisse (fct_order_payment).
-- Des ecarts reels existent dans Olist (bons achat partiels, arrondis) :
-- le test est donc en avertissement et son resultat est COMMENTE dans le
-- rapport plutot que corrige artificiellement.
{{ config(severity='warn') }}

with facture as (

    select order_id, sum(montant_total) as total_facture
    from {{ ref('fct_order_item') }}
    group by order_id

),

encaisse as (

    select order_id, sum(montant_paye) as total_encaisse
    from {{ ref('fct_order_payment') }}
    group by order_id

)

select
    f.order_id,
    f.total_facture,
    e.total_encaisse,
    round(abs(f.total_facture - e.total_encaisse), 2) as ecart_absolu
from facture f
inner join encaisse e on e.order_id = f.order_id
where abs(f.total_facture - e.total_encaisse) > 1.00
