-- Nettoyage du catalogue : ~610 produits sans categorie -> 'inconnu'.
-- Regle : aucune valeur NULL dans un attribut de dimension.
with source as (

    select * from {{ source('raw', 'products') }}

),

typed as (

    select
        product_id::text                                                as product_id,
        coalesce(nullif(trim(product_category_name), ''), 'inconnu')    as product_category_name,
        nullif(trim(product_name_lenght), '')::int                      as product_name_length,
        nullif(trim(product_description_lenght), '')::int               as product_description_length,
        nullif(trim(product_photos_qty), '')::int                       as product_photos_qty,
        nullif(trim(product_weight_g), '')::numeric                     as product_weight_g,
        nullif(trim(product_length_cm), '')::numeric                    as product_length_cm,
        nullif(trim(product_height_cm), '')::numeric                    as product_height_cm,
        nullif(trim(product_width_cm), '')::numeric                     as product_width_cm
    from source
    where product_id is not null

)

select * from typed
