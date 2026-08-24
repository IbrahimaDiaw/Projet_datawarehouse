"""
Couche EXTRACT / LOAD du pipeline.

Principe : les 9 CSV Olist sont charges TELS QUELS dans le schema `raw`,
toutes les colonnes en TEXT, plus une colonne technique `_ingested_at`.

Pourquoi tout en TEXT ?
  - la couche raw doit etre une copie fidele de la source : aucun cast ne doit
    pouvoir faire echouer ou silencieusement alterer l'ingestion ;
  - le typage et le nettoyage sont la responsabilite de la couche staging (dbt),
    ou ils sont versionnes, testes et rejouables.

Usage :  docker compose --profile tools run --rm ingestion
"""

import csv
import io
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
RAW_DIR = Path(os.getenv("RAW_DIR", "/app/data/raw"))
RAW_SCHEMA = "raw"

# fichier CSV source  ->  table cible dans le schema raw
FILE_TO_TABLE = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_customers_dataset.csv": "customers",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "product_category_translation",
}


def get_engine():
    user = os.getenv("POSTGRES_USER", "dwh")
    password = os.getenv("POSTGRES_PASSWORD", "dwh")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "olist_dw")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


# --------------------------------------------------------------------------- #
# Chargement
# --------------------------------------------------------------------------- #
def create_table(conn, table, columns):
    """Cree (ou recree) la table raw avec toutes les colonnes en TEXT."""
    cols_ddl = ",\n    ".join('"{}" TEXT'.format(c) for c in columns)
    conn.execute(text('DROP TABLE IF EXISTS {}."{}" CASCADE'.format(RAW_SCHEMA, table)))
    conn.execute(
        text(
            'CREATE TABLE {}."{}" (\n    {},\n'
            "    _ingested_at TIMESTAMP NOT NULL DEFAULT now()\n)".format(
                RAW_SCHEMA, table, cols_ddl
            )
        )
    )


def copy_dataframe(raw_conn, table, df):
    """Chargement en masse via COPY (bien plus rapide que des INSERT ligne a ligne)."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, quoting=csv.QUOTE_MINIMAL, na_rep="")
    buffer.seek(0)

    cols = ", ".join('"{}"'.format(c) for c in df.columns)
    with raw_conn.cursor() as cur:
        cur.copy_expert(
            "COPY {}.\"{}\" ({}) FROM STDIN WITH (FORMAT csv, NULL '')".format(
                RAW_SCHEMA, table, cols
            ),
            buffer,
        )


def profile(df):
    """Mini-profilage utilise pour le chapitre 'qualite des donnees' du rapport."""
    n = len(df)
    dupes = int(df.duplicated().sum())
    null_cols = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().any()}
    msg = "{:>9,} lignes | {} colonnes | {} doublons stricts".format(n, len(df.columns), dupes)
    if null_cols:
        details = ", ".join("{}={}".format(c, v) for c, v in sorted(null_cols.items()))
        msg += "\n              valeurs manquantes : " + details
    return msg


def main():
    if not RAW_DIR.exists():
        print("[ERREUR] Repertoire introuvable : {}".format(RAW_DIR))
        return 1

    missing = [f for f in FILE_TO_TABLE if not (RAW_DIR / f).exists()]
    if missing:
        print("[ERREUR] Fichiers CSV manquants dans data/raw/ :")
        for f in missing:
            print("         - " + f)
        print(
            "\n  Telecharger le dataset : "
            "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
            "\n  puis dezipper dans data/raw/"
        )
        return 1

    engine = get_engine()
    total_rows = 0

    print("=" * 78)
    print("INGESTION  ->  schema raw")
    print("=" * 78)

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS " + RAW_SCHEMA))

    for filename, table in FILE_TO_TABLE.items():
        path = RAW_DIR / filename
        # dtype=str : aucune inference de type, la source est preservee a l'identique
        df = pd.read_csv(path, dtype=str, keep_default_na=True)

        print("\n[{}]".format(table))
        print("  source      : " + filename)
        print("  profilage   : " + profile(df))

        with engine.begin() as conn:
            create_table(conn, table, list(df.columns))

        raw_conn = engine.raw_connection()
        try:
            copy_dataframe(raw_conn, table, df)
            raw_conn.commit()
        finally:
            raw_conn.close()

        total_rows += len(df)
        print("  charge      : OK -> {}.{}".format(RAW_SCHEMA, table))

    print("\n" + "=" * 78)
    print(
        "TERMINE : {} tables, {:,} lignes chargees dans '{}'.".format(
            len(FILE_TO_TABLE), total_rows, RAW_SCHEMA
        )
    )
    print("Etape suivante : docker compose --profile tools run --rm dbt build")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
