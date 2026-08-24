# Tableau de bord Metabase

## Connexion

<http://localhost:3000> → créer le compte admin → *Ajouter une base de données*

| Champ | Valeur |
|---|---|
| Type | PostgreSQL |
| Hôte | `postgres` |
| Port | `5432` |
| Base | `olist_dw` |
| Utilisateur / mot de passe | `dwh` / `dwh` |
| Schémas | `marts` uniquement |

Ne jamais exposer `raw` ou `staging` dans l'outil de BI : le décideur ne doit voir
que le modèle en étoile.

## Structure attendue — un onglet par question métier

**Onglet 0 — Vue d'ensemble**
Cartes KPI (requête `analyses/q0_kpi_synthese.sql`) : CA total, nombre de commandes,
panier moyen, délai moyen, taux de retard, note moyenne.
Puis la courbe du CA mensuel avec la croissance YoY en second axe.

**Onglet 1 — Croissance** (`q1`, `q1b`)
Courbe CA mensuel · barres empilées CA par région et trimestre · carte du Brésil par état.

**Onglet 2 — Produits** (`q2`)
Barres horizontales du CA par catégorie · courbe de Pareto cumulée (part cumulée %)
· treemap segment → catégorie.

**Onglet 3 — Logistique** (`q3`)
Carte choroplèthe du délai moyen par état · barres du taux de retard
· histogramme de distribution des délais · table des vendeurs les plus lents.

**Onglet 4 — Satisfaction** (`q4`)
Barres de la note moyenne par tranche de retard *(le graphique le plus parlant du
projet)* · matrice catégorie × note · évolution de la note dans le temps.

**Onglet 5 — Clients** (`q5`)
Camembert des moyens de paiement · barres des tranches d'échéances
· répartition des segments de fidélité.

## Filtres interactifs à câbler sur chaque onglet

- Période → `dim_date.date_day`
- Région / État → `dim_customer.region`, `dim_customer.etat`
- Segment / Catégorie → `dim_product.segment`, `dim_product.categorie`
- Statut de commande → `dim_order_status.famille_statut`

L'interactivité est explicitement notée : chaque filtre doit se propager à tous les
visuels de l'onglet.

## Captures pour le rapport

Enregistrer les captures dans ce dossier sous `onglet_0_synthese.png`, etc.
