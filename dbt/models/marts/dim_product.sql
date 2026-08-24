-- Dimension produit DENORMALISEE (schema en etoile) : la categorie et son
-- libelle anglais sont portes directement par la dimension.
-- La variante en FLOCON consisterait a extraire une table dim_category
-- reliee par category_key ; la comparaison est developpee dans le rapport.
with products as (

    select * from {{ ref('stg_products') }}

),

categories as (

    select * from {{ ref('stg_product_category') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['p.product_id']) }} as product_key,
    p.product_id,
    p.product_category_name                                         as categorie_pt,
    coalesce(c.product_category_name_en, p.product_category_name)   as categorie,

    -- regroupement metier de haut niveau (hierarchie Segment > Categorie)
    case
        when p.product_category_name like '%informatica%'
          or p.product_category_name like '%eletronicos%'
          or p.product_category_name like '%telefonia%'
          or p.product_category_name like '%pc_gamer%'          then 'High-tech'
        when p.product_category_name like '%casa%'
          or p.product_category_name like '%moveis%'
          or p.product_category_name like '%cama_mesa_banho%'
          or p.product_category_name like '%construcao%'        then 'Maison'
        when p.product_category_name like '%moda%'
          or p.product_category_name like '%fashion%'           then 'Mode'
        when p.product_category_name like '%beleza%'
          or p.product_category_name like '%perfumaria%'
          or p.product_category_name like '%saude%'             then 'Beaute-Sante'
        when p.product_category_name like '%esporte%'
          or p.product_category_name like '%brinquedos%'
          or p.product_category_name like '%lazer%'             then 'Sport-Loisirs'
        when p.product_category_name = 'inconnu'                then 'Inconnu'
        else 'Autres'
    end                                                             as segment,

    p.product_weight_g                                              as poids_g,
    (p.product_length_cm * p.product_height_cm * p.product_width_cm) as volume_cm3,
    p.product_photos_qty                                            as nb_photos,
    p.product_description_length                                    as longueur_description,

    case
        when p.product_weight_g is null      then 'Inconnu'
        when p.product_weight_g < 500        then 'Leger (<0,5 kg)'
        when p.product_weight_g < 2000       then 'Moyen (0,5-2 kg)'
        when p.product_weight_g < 10000      then 'Lourd (2-10 kg)'
        else                                      'Tres lourd (>10 kg)'
    end                                                             as tranche_poids

from products p
left join categories c on c.product_category_name = p.product_category_name
