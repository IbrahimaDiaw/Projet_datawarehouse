# Plan du rapport de projet (10 à 15 pages)

Correspondance exacte avec les livrables exigés par le sujet.

---

## Page de garde
Titre, module, noms, année universitaire, lien du dépôt Git.

## 1. Introduction et présentation du dataset — 1,5 p
- Contexte : marketplace Olist, 100 000 commandes réelles, 2016-2018.
- Description des 9 fichiers sources (tableau : fichier, volume, clé, rôle).
- Justification du choix : richesse relationnelle, plusieurs grains, anomalies réelles.

## 2. Objectifs métier — 1 p
- Les 5 questions décisionnelles.
- Pour chacune : décideur concerné, indicateur cible, décision qu'elle éclaire.
- **Tableau de traçabilité** question → mesures → dimensions → visuel du dashboard.
  *(C'est ce tableau qui prouve la cohérence de tout le projet.)*

## 3. Modélisation multidimensionnelle — 3 p
- Démarche : identification des processus métier, puis du grain, puis des dimensions, puis des faits.
- **Déclaration explicite du grain** de chacune des 3 tables de faits.
- Diagramme de la constellation (généré depuis `docs/modele_dimensionnel.dbml`).
- Typologie des mesures : additives / non additives (les délais) — et conséquence
  directe : `sum()` interdit sur les délais, `avg()` obligatoire.
- Notions avancées mobilisées : dimension dégénérée (`order_id`), *junk dimension*
  (`dim_order_status`), dimension temps générée, SCD type 1 et justification.
- **Étoile vs flocon** : choix de l'étoile, ce que donnerait le flocon sur
  `dim_product`, arbitrage lisibilité / redondance / performance des jointures.

## 4. Architecture technique — 2 p
- Schéma en couches raw → staging → intermediate → marts → BI.
- Justification outil par outil (tableau du README) : pourquoi PostgreSQL,
  pourquoi dbt **plutôt que Pentaho PDI vu en cours** — versionnage Git, tests
  automatisés, lignage généré, reproductibilité par conteneur.
- Capture du **graphe de lignage** produit par `dbt docs`.

## 5. Stratégie de contrôle qualité — 2,5 p
- Les deux niveaux : tests déclaratifs et tests métier singuliers.
- Tableau des 6 anomalies réelles : anomalie → détection → règle de gestion → impact
  si non traitée. *Insister sur le piège `customer_id` / `customer_unique_id` et sur
  la duplication de `geolocation` : ce sont les deux erreurs qui faussent le CA.*
- Capture de la sortie de `dbt build` (nombre de tests exécutés, avertissements).
- Ce qu'on a choisi de **ne pas** corriger et pourquoi (écarts CA/paiements).

## 6. Résultats d'analyse — 3 p
Une sous-section par question métier : la requête, le résultat, la **lecture métier**.
- 6.1 Croissance du CA — saisonnalité, effet Black Friday nov. 2017, YoY.
- 6.2 Concentration du catalogue — courbe de Pareto, part des catégories cœur.
- 6.3 Performance logistique — écart Sudeste / Norte, délai promis vs réel.
- 6.4 Retard et satisfaction — la note chute avec le retard : quantifier l'effet.
- 6.5 Comportement d'achat — paiement en plusieurs fois, très faible récurrence client.

## 7. Tableau de bord — 1,5 p
Captures commentées des 5 onglets, description des filtres interactifs,
et rappel du lien avec les questions métier.

## 8. Synthèse et enseignements — 1 p
- Recommandations métier concrètes issues des analyses.
- Difficultés rencontrées et arbitrages (grain, gestion des NULL, période retenue).
- Limites : dataset historique figé, pas de coût d'achat donc pas de marge réelle,
  absence d'historique pour un vrai SCD type 2.
- Pistes d'industrialisation : orchestration (Airflow), incrémental, CI sur les tests.

## Annexes
Requêtes SQL complètes, dictionnaire des données, commandes de reproduction.

---

### Contrôle avant remise
- [ ] Le grain de chaque fait est écrit noir sur blanc
- [ ] Le diagramme du modèle est lisible en pleine page
- [ ] Chaque question métier a sa réponse chiffrée ET son visuel
- [ ] Le choix des outils est justifié, pas seulement listé
- [ ] Les captures de `dbt build` et du lignage sont présentes
- [ ] Le dépôt Git est public ou accessible, avec un README qui permet de tout rejouer
