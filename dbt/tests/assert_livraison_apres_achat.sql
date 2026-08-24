-- CONTROLE DE COHERENCE TEMPORELLE
-- Une commande ne peut pas etre livree avant avoir ete passee.
-- Ce test protege contre une erreur de mapping de colonnes lors de
-- ingestion (inversion de deux timestamps).
select
    order_id,
    date_achat,
    date_livraison,
    delai_livraison_jours
from {{ ref('fct_order_item') }}
where date_livraison is not null
  and date_livraison < date_achat
