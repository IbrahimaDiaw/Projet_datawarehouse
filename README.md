# Pipeline Analytics Olist — Entrepôt de données & Reporting

> Projet 2 — Master 1 MBDA, UFC/UNCHK 2026
> Module : Bases de données multidimensionnelles

Chaîne complète **Data / Data Warehouse / Business Intelligence** construite sur le
dataset e-commerce brésilien **Olist** : ingestion des sources, modélisation en
étoile, tests de qualité automatisés et tableau de bord interactif.

---

## 1. Questions métier

| # | Question | Objet analysé |
|---|----------|---------------|
| 1 | Comment évolue le CA par mois/trimestre et par région, et quelle croissance MoM / YoY ? | `fct_order_item` × `dim_date` × `dim_customer` |
| 2 | Quelles catégories concentrent le CA ? La loi de Pareto se vérifie-t-elle ? | `fct_order_item` × `dim_product` |
| 3 | Quel délai de livraison par état/vendeur et quel taux de retard vs promesse ? | `fct_order_item` × `dim_customer` × `dim_seller` |
| 4 | Quel est l'impact du retard de livraison sur la satisfaction client ? | `fct_order_review` |
| 5 | Panier moyen, clients récurrents, moyens de paiement et échéances ? | `fct_order_payment` × `dim_customer` |

Les requêtes correspondantes sont dans [`analyses/`](analyses/).

## 2. Architecture

```
CSV Kaggle (9 fichiers)
   │  ingestion/load_raw.py  (Python + COPY)
   ▼
schéma raw          copie fidèle, tout en TEXT + _ingested_at
   │  dbt
   ▼
schéma staging      typage, nettoyage, déduplication      (vues)
   │
   ▼
schéma intermediate logique métier réutilisable           (vues)
   │
   ▼
schéma marts        modèle en étoile : dim_* et fct_*     (tables)
   │
   ▼
Metabase            tableau de bord interactif
```

| Couche | Outil | Justification |
|---|---|---|
| Stockage | PostgreSQL 16 | SGBD relationnel robuste, gratuit, SQL analytique complet (fonctions de fenêtrage, percentiles) |
| Ingestion | Python + pandas + `COPY` | Chargement en masse rapide, profilage des sources intégré au script |
| Transformation | dbt 1.12.3 (version figée) | Modèles versionnés en SQL, **tests de qualité déclaratifs**, lignage automatique, documentation générée |
| Restitution | Streamlit + Plotly | Dashboard interactif **versionné dans le dépôt** (un tableau Metabase vit dans sa base interne et ne se livre pas en Git) |
| Exécution | Docker Compose | Reproductibilité totale : l'environnement complet démarre en une commande |

## 3. Modèle dimensionnel

**Constellation de faits** : trois tables de faits de grains différents partageant
les mêmes dimensions conformes.

| Table de faits | Grain | Volume |
|---|---|---|
| `fct_order_item` | **1 ligne = 1 article d'une commande** | ~112 650 |
| `fct_order_payment` | 1 ligne = 1 moyen de paiement d'une commande | ~103 900 |
| `fct_order_review` | 1 ligne = 1 avis (1 commande notée) | ~98 400 |

**Dimensions** : `dim_date` (générée), `dim_customer` (SCD type 1),
`dim_product`, `dim_seller`, `dim_order_status` (*junk dimension*).
`order_id` est conservé dans les faits comme **dimension dégénérée**.

Le diagramme se génère à partir de [`docs/modele_dimensionnel.dbml`](docs/modele_dimensionnel.dbml)
sur [dbdiagram.io](https://dbdiagram.io).

## 4. Démarrage

### Prérequis
Docker Desktop. Rien d'autre à installer : Python et dbt s'exécutent en conteneur.

### Étape 0 — Configuration
```bash
cp .env.example .env
```

### Étape 1 — Données sources
Télécharger le dataset [Brazilian E-Commerce (Olist)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
et dézipper les 9 fichiers CSV dans `data/raw/`.

### Étape 2 — Démarrer l'infrastructure
```bash
docker compose up -d postgres metabase
```

### Étape 3 — Ingestion (Extract / Load)
```bash
docker compose --profile tools run --rm ingestion
```

### Étape 4 — Transformation et tests (Transform)
```bash
docker compose --profile tools run --rm dbt deps
docker compose --profile tools run --rm dbt build
```
`dbt build` exécute les modèles **puis** l'intégralité des tests de qualité.

### Étape 5 — Tableau de bord
```bash
docker compose up -d --build dashboard
```
Puis <http://localhost:8501>. Six onglets (synthèse + une page par question métier)
avec filtres globaux : période, région, segment produit, exclusion des commandes annulées.

**Metabase (optionnel, exploration ad hoc)** : `docker compose up -d metabase`, puis
<http://localhost:3000>. Son assistant demande de créer un compte administrateur ;
connecter ensuite la base — hôte `postgres`, port `5432`, base `olist_dw`, schéma
`marts` uniquement. Le dashboard livrable reste celui de Streamlit, car il est
versionné dans le dépôt alors qu'un tableau Metabase vit dans sa base interne.

### Compilation du rapport PDF
```bash
docker compose --profile tools run --rm report
```
Regénère `docs/rapport.pdf` (16 pages) depuis `docs/rapport.md` et `docs/rapport.css`.

### Documentation et lignage
```bash
docker compose --profile tools run --rm --service-ports dbt docs generate
docker compose --profile tools run --rm --service-ports dbt docs serve --port 8080 --host 0.0.0.0
```
Puis <http://localhost:8080> — le graphe de lignage est une capture à intégrer au rapport.

## 5. Stratégie de qualité des données

Deux niveaux de contrôle, tous rejouables par `dbt test` :

**Tests déclaratifs** (dans les fichiers `_*.yml`) : unicité, non-nullité,
intégrité référentielle entre chaque fait et chaque dimension, valeurs acceptées,
plages de valeurs.

**Tests métier singuliers** (dans [`dbt/tests/`](dbt/tests/)) :

| Test | Contrôle |
|---|---|
| `assert_pas_de_perte_de_lignes` | Le fait contient autant de lignes que la source (détecte une jointure fautive) |
| `assert_client_unique_par_commande` | Une commande = un seul client (détecte un produit cartésien) |
| `assert_livraison_apres_achat` | Cohérence chronologique des timestamps |
| `assert_coherence_ca_paiements` | Montant facturé ≈ montant encaissé (*warn*) |
| `assert_volumetrie_mensuelle` | Détecte les mois anormalement creux (*warn*) |

**Anomalies traitées** (documentées dans le rapport) :

1. `customer_id` est une clé **par commande** → la dimension client est bâtie sur `customer_unique_id`.
2. `geolocation` contient ~1 M de lignes pour ~19 000 codes postaux → agrégation **avant** jointure.
3. ~610 produits sans catégorie → valeur de substitution `inconnu`.
4. ~2 965 commandes sans date de livraison → conservées, exclues des KPI logistiques via un drapeau.
5. Fin 2016 quasi vide → période d'analyse restreinte à 2017-01 → 2018-08.
6. Avis en double → un seul avis conservé par commande (le plus récent).

## 6. Arborescence

```
projet-dw-olist/
├── docker-compose.yml        infrastructure complète
├── docker/                   images ingestion et dbt, init PostgreSQL
├── data/raw/                 CSV Olist (non versionnés)
├── ingestion/                Extract / Load en Python
├── dbt/
│   ├── models/staging/       typage et nettoyage
│   ├── models/intermediate/  logique métier
│   ├── models/marts/         modèle en étoile
│   ├── seeds/                référentiel des états brésiliens
│   └── tests/                tests de qualité singuliers
├── analyses/                 requêtes des 5 questions métier
├── dashboard/               application Streamlit (app.py)
└── docs/                     modèle dimensionnel, rapport
```

## 7. Livrables

- [x] Code source (ce dépôt)
- [x] Rapport PDF ([docs/rapport.pdf](docs/rapport.pdf)) — source Markdown versionnée, à personnaliser (nom, URL du dépôt, captures)
- [x] Tableau de bord interactif (`dashboard/app.py`)
- [ ] Captures du dashboard pour le rapport
