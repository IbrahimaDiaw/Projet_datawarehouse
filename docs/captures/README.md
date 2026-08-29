# Captures d'écran des tableaux de bord

Déposer les images ici en respectant **exactement** ces noms : le script de
compilation du rapport les insère automatiquement au §7.

## Dashboard Streamlit (livrable versionné) — <http://localhost:8501>

| Fichier attendu | Onglet |
|---|---|
| `st0_synthese.png` | Synthèse — 6 cartes KPI + CA mensuel |
| `st1_croissance.png` | Croissance — MoM, panier moyen, CA trimestriel |
| `st2_produits.png` | Produits — courbe de Pareto, treemap |
| `st3_logistique.png` | Logistique — nuage délai × retard |
| `st4_satisfaction.png` | Satisfaction — note par tranche de retard |
| `st5_clients.png` | Clients — paiements, fidélité |

## Dashboard Metabase — <http://localhost:3000/dashboard/2>

| Fichier attendu | Vue |
|---|---|
| `mb_dashboard.png` | Vue d'ensemble : filtres + KPI + bloc Question 1 |
| `mb_filtres.png` | *(optionnel)* Le même tableau avec un filtre actif, pour démontrer l'interactivité |

## Conseils de prise de vue

- Format **PNG**, largeur **1400 px minimum** — en dessous, le texte des
  graphiques devient illisible une fois réduit dans le PDF.
- Masquer la barre d'outils du navigateur (F11 plein écran, ou le mode
  « Passer en plein écran » du menu ⋯ de Metabase).
- Pour Streamlit, faire défiler jusqu'en haut de l'onglet avant la capture.
- Écarter la souris des graphiques : une infobulle Plotly ouverte gâche l'image.

Une fois les fichiers déposés, relancer :

```
docker compose --profile tools run --rm report   # PDF
docker compose --profile tools run --rm word     # Word
```
