# Résultats d'analyse — exécution du 24/08/2026

Pipeline exécuté sur les données réelles : **1 550 922 lignes** ingérées,
19 modèles construits, **123 tests passés, 2 avertissements, 0 erreur**.

Période d'analyse : **2017-01 → 2018-08** (justification en §5).
Montants en réal brésilien (R$).

---

## KPI de synthèse

| Indicateur | Valeur |
|---|---|
| Chiffre d'affaires | **15 614 484 R$** |
| Commandes | 97 604 |
| Clients | 94 416 |
| Panier moyen | **159,98 R$** |
| Délai moyen de livraison | 12,5 jours |
| Taux de retard vs promesse | 7,9 % |
| Note moyenne | 4,09 / 5 |
| Clients récurrents | **3,1 %** |

## Q1 — Croissance

Le CA passe de **134 k R$ (janv. 2017) à ~1 000 k R$ (août 2018)**, soit une
multiplication par 7,4 en 20 mois.

| Fait marquant | Lecture |
|---|---|
| Nov. 2017 : 1 167 k R$, +53,5 % MoM | Pic **Black Friday**, plus haut mois de l'historique |
| Déc. 2017 : −26,9 % MoM | Contrecoup post-Black Friday, pas un décrochage |
| YoY janv. 2018 : **+716 %** | Effet de base : 2017 démarrait quasi de zéro |
| YoY août 2018 : +51,9 % | Croissance qui se normalise |
| 2018 : plateau ~1 000-1 150 k R$/mois | **Maturation** : la croissance explosive s'arrête début 2018 |

Le panier moyen reste remarquablement stable (146-173 R$) : la croissance vient
du **volume de commandes**, pas de la valeur unitaire.

## Q2 — Concentration du catalogue

**17 catégories sur 74 (23 %) génèrent 80 % du CA.** La loi de Pareto se vérifie,
en version légèrement plus concentrée que le 80/20 canonique.

| Rang | Catégorie | CA | Part | Cumul |
|---|---|---|---|---|
| 1 | health_beauty | 1 430 k | 9,16 % | 9,16 % |
| 2 | watches_gifts | 1 289 k | 8,25 % | 17,41 % |
| 3 | bed_bath_table | 1 239 k | 7,94 % | 25,35 % |
| 4 | sports_leisure | 1 140 k | 7,30 % | 32,65 % |
| 5 | computers_accessories | 1 045 k | 6,69 % | 39,34 % |
| … | | | | |
| 17 | pet_shop | 252 k | 1,61 % | **79,82 %** |

Le **poids du transport** varie du simple au quintuple : 4,2 % du montant pour
`computers` (panier à 1 098 R$) contre 20,0 % pour `office_furniture`. C'est un
levier de marge directement actionnable.

Cas notable : `computers` réalise 233 k R$ avec seulement **203 articles**
(prix moyen 1 098 R$) — faible volume, forte valeur.

## Q3 — Performance logistique

Écart de **1 à 3,2** entre le meilleur et le pire état.

| | État | Délai moyen | Taux de retard |
|---|---|---|---|
| Meilleur | São Paulo (40 410 cmd) | **8,7 j** | 5,8 % |
| | Minas Gerais | 12,0 j | 5,5 % |
| | Rio de Janeiro | 15,1 j | 13,0 % |
| Pire | Amapá (Norte) | **28,2 j** | 4,9 % |
| | Amazonas | 26,4 j | 4,3 % |

**Résultat contre-intuitif à souligner dans le rapport** : les états les plus
lents ne sont *pas* les plus en retard. Le Norte livre en 26-28 jours mais tient
sa promesse (retard 3-5 %) car la date estimée y est très prudente (41-46 j).
À l'inverse, **Alagoas** (Nordeste) affiche **24,2 % de retard** avec une promesse
de 32,5 jours trop optimiste.

→ Le problème n'est pas la vitesse de livraison mais la **calibration de la
promesse client**. L'écart moyen est de −10 à −20 jours : Olist sous-promet
systématiquement.

## Q4 — Impact du retard sur la satisfaction

C'est le résultat le plus net du projet : **la note s'effondre dès que le retard
dépasse 3 jours**.

| Tranche de retard | Avis | Part | Note | Satisfaits | Insatisfaits |
|---|---|---|---|---|---|
| Très en avance | 56 674 | 57,6 % | **4,32** | 83,7 % | 8,9 % |
| En avance | 26 531 | 27,0 % | 4,26 | 81,9 % | 9,4 % |
| À l'heure | 4 703 | 4,8 % | 4,13 | 77,4 % | 11,2 % |
| Retard léger (≤3 j) | 2 633 | 2,7 % | 3,76 | 66,2 % | 19,2 % |
| Retard moyen (3-10 j) | 2 790 | 2,8 % | **2,12** | 22,8 % | 66,9 % |
| Retard important (>10 j) | 2 230 | 2,3 % | **1,70** | 11,8 % | 79,2 % |
| Non livré | 2 769 | 2,8 % | 1,75 | 14,4 % | 77,8 % |

**Effet de seuil brutal** : entre « retard léger » et « retard moyen », la note
chute de 3,76 à 2,12 (−1,64 point) et l'insatisfaction triple (19 % → 67 %).
Un retard de plus de 3 jours coûte donc **2 points de note**, autant qu'une
non-livraison pure et simple.

Recommandation : allonger les délais annoncés est moins coûteux que de les tenir.

## Q5 — Comportement d'achat

**Moyens de paiement**

| Moyen | Montant | Part |
|---|---|---|
| Carte de crédit | 12 494 k R$ | **78,4 %** |
| Boleto (virement) | 2 860 k R$ | 17,9 % |
| Bon d'achat | 374 k R$ | 2,3 % |
| Carte de débit | 218 k R$ | 1,4 % |

**Paiement fractionné** — 49,4 % des paiements sont échelonnés :

| Échéances | Part | Montant moyen |
|---|---|---|
| Comptant | 50,6 % | 112 R$ |
| 2-3 fois | 22,0 % | 134 R$ |
| 4-6 fois | 15,6 % | 181 R$ |
| 7-12 fois | 11,6 % | **333 R$** |

Corrélation nette : **plus le panier est élevé, plus le client fractionne**
(112 R$ comptant → 333 R$ en 7-12 fois). Le crédit est un levier de panier.

**Fidélité — le point faible du modèle**

| Segment | Clients | Part |
|---|---|---|
| Achat unique | 93 099 | **96,88 %** |
| 2 commandes | 2 745 | 2,86 % |
| 3 et plus | 252 | 0,26 % |

Moins de **3,2 %** des clients repassent commande. La croissance repose
intégralement sur l'acquisition, jamais sur la rétention — la vulnérabilité
stratégique majeure de la marketplace.

---

## Les deux avertissements de `dbt build`

Ils ne sont pas des défauts du pipeline mais des **constats documentés**.

**1. `assert_volumetrie_mensuelle` — 3 mois sous le seuil**

| Mois | Commandes |
|---|---|
| 2016-09 | 3 |
| 2016-12 | 1 |
| 2018-09 | 1 |

Ce sont des artefacts de bornes du dataset. C'est précisément ce test qui
**justifie objectivement** la période d'analyse retenue (2017-01 → 2018-08).

**2. `assert_coherence_ca_paiements` — 249 commandes en écart**

| Commandes concernées | Part | Écart moyen | Écart max | Écart total |
|---|---|---|---|---|
| 249 | 0,25 % | 13,10 R$ | 182,81 R$ | 3 262 R$ |

3 262 R$ d'écart sur 15,6 M R$ de CA, soit **0,02 %**. Cause probable : bons
d'achat partiels et arrondis. L'écart est **conservé et documenté** plutôt que
corrigé artificiellement — décision à assumer et expliquer en soutenance.
