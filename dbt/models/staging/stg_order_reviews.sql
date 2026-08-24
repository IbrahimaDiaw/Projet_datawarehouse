-- Deduplication : quelques review_id apparaissent plusieurs fois et certaines
-- commandes portent plusieurs avis. Regle retenue : on conserve l avis le plus
-- recent de chaque commande, ce qui garantit le grain "1 ligne = 1 commande notee".
with source as (

    select * from {{ source('raw', 'order_reviews') }}

),

typed as (

    select
        review_id::text                                         as review_id,
        order_id::text                                          as order_id,
        nullif(trim(review_score), '')::int                     as review_score,
        nullif(trim(review_comment_title), '')                  as review_comment_title,
        nullif(trim(review_comment_message), '')                as review_comment_message,
        nullif(trim(review_creation_date), '')::timestamp       as review_creation_ts,
        nullif(trim(review_answer_timestamp), '')::timestamp    as review_answer_ts
    from source
    where review_id is not null
      and order_id is not null

),

deduplicated as (

    select
        typed.*,
        row_number() over (
            partition by order_id
            order by review_creation_ts desc nulls last, review_id
        ) as rn
    from typed

)

select
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_ts,
    review_answer_ts,
    (review_comment_message is not null) as has_comment
from deduplicated
where rn = 1
