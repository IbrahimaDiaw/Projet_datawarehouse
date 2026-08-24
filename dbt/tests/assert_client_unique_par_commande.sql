-- CONTROLE DE GRAIN
-- Une commande donnee doit etre rattachee a un seul et unique client.
-- Si ce test echoue, la jointure customer_id -> customer_unique_id a
-- duplique des lignes et le chiffre d affaires est surevalue.
select
    order_id,
    count(distinct customer_key) as nb_clients_distincts
from {{ ref('fct_order_item') }}
group by order_id
having count(distinct customer_key) > 1
