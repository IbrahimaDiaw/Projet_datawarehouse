"""
Generation des figures du rapport (docs/figures/*.png).

Les graphiques sont produits a partir du schema `marts`, donc des memes
donnees que le tableau de bord : le rapport ne peut pas diverger du pipeline.
Regeneration : docker compose --profile tools run --rm figures
"""

import os
import warnings
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")

SORTIE = Path(__file__).resolve().parent / "figures"
SORTIE.mkdir(exist_ok=True)

BLEU, ORANGE, VERT, ROUGE, GRIS = "#2E5EAA", "#F4A261", "#2A9D8F", "#E76F51", "#C9D6E8"
LARGEUR, HAUTEUR, ECHELLE = 1000, 460, 2

MISE_EN_PAGE = dict(
    font=dict(family="DejaVu Sans, Arial", size=13, color="#1a1a1a"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=70, r=60, t=100, b=60),
    title=dict(font=dict(size=15, color="#12315c"), y=0.95, yanchor="top"),
)
AXE = dict(showgrid=True, gridcolor="#e8edf4", zeroline=False, linecolor="#b9c4d4")


def engine():
    return create_engine(
        "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            os.getenv("POSTGRES_USER", "dwh"),
            os.getenv("POSTGRES_PASSWORD", "dwh"),
            os.getenv("POSTGRES_HOST", "postgres"),
            os.getenv("POSTGRES_PORT", "5432"),
            os.getenv("POSTGRES_DB", "olist_dw"),
        )
    )


def q(sql):
    raw = engine().raw_connection()
    try:
        return pd.read_sql(sql, raw)
    finally:
        raw.close()


def sauver(fig, nom):
    fig.update_layout(**MISE_EN_PAGE)
    fig.update_xaxes(**AXE)
    fig.update_yaxes(**AXE)
    chemin = SORTIE / f"{nom}.png"
    fig.write_image(str(chemin), width=LARGEUR, height=HAUTEUR, scale=ECHELLE)
    print(f"  {chemin.name}  ({chemin.stat().st_size // 1024} Ko)")


FILTRE = """
    from marts.fct_order_item f
    join marts.dim_date d          on d.date_key = f.order_date_key
    join marts.dim_customer c      on c.customer_key = f.customer_key
    join marts.dim_product p       on p.product_key = f.product_key
    join marts.dim_order_status s  on s.status_key = f.status_key
    where d.is_periode_analyse and s.is_chiffre_affaires
"""


# --------------------------------------------------------------------------- #
def fig_croissance():
    """6.1 - Chiffre d'affaires mensuel, volume de commandes et croissance MoM."""
    m = q(f"""
        with base as (
            select d.annee_mois, sum(f.montant_total) ca,
                   count(distinct f.order_id) commandes
            {FILTRE} group by d.annee_mois
        )
        select annee_mois, ca, commandes,
               100.0*(ca - lag(ca) over (order by annee_mois))
                   / nullif(lag(ca) over (order by annee_mois),0) mom
        from base order by annee_mois
    """)

    fig = go.Figure()
    fig.add_bar(x=m.annee_mois, y=m.commandes, name="Commandes",
                marker_color=GRIS, yaxis="y2")
    fig.add_scatter(x=m.annee_mois, y=m.ca, name="Chiffre d'affaires",
                    line=dict(color=BLEU, width=3.5), mode="lines+markers")
    fig.add_annotation(x="2017-11", y=float(m.loc[m.annee_mois == "2017-11", "ca"].iloc[0]),
                       text="Black Friday<br>+53,5 %", showarrow=True, arrowhead=2,
                       ax=-45, ay=-45, font=dict(size=12, color=ROUGE),
                       arrowcolor=ROUGE, bgcolor="white", bordercolor=ROUGE)
    fig.update_layout(
        title="Chiffre d'affaires et volume de commandes par mois",
        yaxis=dict(title="CA (R$)", **AXE),
        yaxis2=dict(title="Commandes", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
    )
    sauver(fig, "fig1_croissance")


def fig_mom():
    """6.1 - Croissance mois sur mois."""
    m = q(f"""
        with base as (
            select d.annee_mois, sum(f.montant_total) ca {FILTRE} group by d.annee_mois
        )
        select annee_mois,
               100.0*(ca - lag(ca) over (order by annee_mois))
                   / nullif(lag(ca) over (order by annee_mois),0) mom
        from base order by annee_mois
    """).dropna()

    couleurs = [VERT if v >= 0 else ROUGE for v in m.mom]
    fig = go.Figure(go.Bar(x=m.annee_mois, y=m.mom, marker_color=couleurs,
                           text=m.mom.round(0).astype(int).astype(str) + " %",
                           textposition="outside", textfont=dict(size=10)))
    fig.update_layout(
        title="Croissance mensuelle du chiffre d'affaires (%)",
        yaxis=dict(title="Variation MoM (%)", **AXE), showlegend=False,
    )
    sauver(fig, "fig2_mom")


def fig_pareto():
    """6.2 - Concentration du chiffre d'affaires par categorie."""
    p = q(f"""
        with base as (
            select p.categorie, sum(f.montant_total) ca {FILTRE} group by p.categorie
        )
        select categorie, ca,
               100.0*sum(ca) over (order by ca desc rows unbounded preceding)
                   / sum(ca) over () cumul
        from base order by ca desc limit 20
    """)

    fig = go.Figure()
    fig.add_bar(x=p.categorie, y=p.ca, name="CA", marker_color=BLEU)
    fig.add_scatter(x=p.categorie, y=p.cumul, name="Part cumulee",
                    yaxis="y2", line=dict(color=ORANGE, width=3.5), mode="lines+markers")
    fig.add_hline(y=80, line_dash="dot", line_color=ROUGE, line_width=2, yref="y2",
                  annotation_text="seuil 80 %", annotation_position="top left",
                  annotation_font_color=ROUGE)
    fig.update_layout(
        title="Courbe de Pareto : 17 categories sur 74 realisent 80 % du CA",
        yaxis=dict(title="CA (R$)", **AXE),
        yaxis2=dict(title="Part cumulee (%)", overlaying="y", side="right",
                    range=[0, 105], showgrid=False),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
        xaxis=dict(tickangle=-40, **AXE),
        margin=dict(l=70, r=60, t=100, b=140),
    )
    sauver(fig, "fig3_pareto")


def fig_logistique():
    """6.3 - Vitesse de livraison contre respect de la promesse."""
    g = q("""
        select c.region, c.etat, count(distinct f.order_id) commandes,
               avg(f.delai_livraison_jours) delai,
               100.0*avg(f.is_retard::numeric) retard
        from marts.fct_order_item f
        join marts.dim_date d          on d.date_key = f.order_date_key
        join marts.dim_customer c      on c.customer_key = f.customer_key
        join marts.dim_order_status s  on s.status_key = f.status_key
        where d.is_periode_analyse and s.is_livree
        group by c.region, c.etat
        having count(distinct f.order_id) >= 50
    """)

    couleurs = {"Sudeste": BLEU, "Sul": VERT, "Centro-Oeste": ORANGE,
                "Nordeste": ROUGE, "Norte": "#8D6E97"}

    # Seuls les etats commentes dans le rapport sont etiquetes : au-dela,
    # les libelles se chevauchent et la figure devient illisible.
    NOMMES = {"Sao Paulo", "Minas Gerais", "Rio de Janeiro", "Alagoas",
              "Maranhao", "Ceara", "Amazonas", "Amapa"}
    # Taille proportionnelle a l aire, plafonnee : Sao Paulo (40 410 commandes)
    # ecraserait sinon toutes les autres bulles.
    ref = 2.0 * g.commandes.max() / (38.0 ** 2)

    fig = go.Figure()
    for region, sous in g.groupby("region"):
        fig.add_scatter(
            x=sous.delai, y=sous.retard, mode="markers+text", name=region,
            text=[e if e in NOMMES else "" for e in sous.etat],
            textposition="top center", textfont=dict(size=10, color="#333"),
            marker=dict(size=sous.commandes, sizemode="area", sizeref=ref,
                        sizemin=5, color=couleurs.get(region, GRIS),
                        line=dict(width=1, color="white"), opacity=0.8),
        )
    fig.update_layout(
        title="Delai de livraison et taux de retard par etat "
              "(taille = volume de commandes)",
        xaxis=dict(title="Delai moyen de livraison (jours)", **AXE),
        yaxis=dict(title="Commandes en retard (%)", range=[0, 28], **AXE),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
    )
    sauver(fig, "fig4_logistique")


def fig_satisfaction():
    """6.4 - Effet du retard sur la note client (figure centrale du rapport)."""
    ordre = ["tres en avance", "en avance", "a l heure", "retard leger",
             "retard moyen", "retard important", "non livre"]
    etiquettes = {"tres en avance": "Tres en<br>avance", "en avance": "En avance",
                  "a l heure": "A l'heure", "retard leger": "Retard leger<br>(<= 3 j)",
                  "retard moyen": "Retard moyen<br>(3-10 j)",
                  "retard important": "Retard important<br>(> 10 j)",
                  "non livre": "Non livre"}

    s = q("""
        select r.tranche_retard, count(*) avis, avg(r.note) note,
               100.0*avg(r.is_insatisfait::int::numeric) insatisfaits
        from marts.fct_order_review r
        join marts.dim_date d on d.date_key = r.order_date_key
        where d.is_periode_analyse
        group by r.tranche_retard
    """)
    s["rang"] = s.tranche_retard.apply(lambda x: ordre.index(x) if x in ordre else 99)
    s = s.sort_values("rang")
    s["libelle"] = s.tranche_retard.map(etiquettes)

    couleurs = [VERT if n >= 4 else (ORANGE if n >= 3 else ROUGE) for n in s.note]
    fig = go.Figure()
    fig.add_bar(x=s.libelle, y=s.note, marker_color=couleurs,
                text=s.note.round(2).astype(str), textposition="outside",
                name="Note moyenne", textfont=dict(size=12))
    fig.add_scatter(x=s.libelle, y=s.insatisfaits, yaxis="y2",
                    name="Clients insatisfaits", mode="lines+markers",
                    line=dict(color="#12315c", width=2.5, dash="dot"))
    fig.add_vline(x=2.5, line_dash="dash", line_color="#999", line_width=2)
    fig.add_annotation(x=3.4, y=4.6, text="Effet de seuil : -1,64 point",
                       showarrow=False, font=dict(size=12, color=ROUGE),
                       bgcolor="white", bordercolor=ROUGE, borderpad=4)
    fig.update_layout(
        title="La note client s'effondre au-dela de 3 jours de retard",
        yaxis=dict(title="Note moyenne / 5", range=[0, 5.2], **AXE),
        yaxis2=dict(title="Insatisfaits (%)", overlaying="y", side="right",
                    range=[0, 104], showgrid=False,
                    tickvals=[0, 20, 40, 60, 80, 100]),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
    )
    sauver(fig, "fig5_satisfaction")


def fig_paiement():
    """6.5 - Fractionnement du paiement et montant moyen."""
    ordre = ["Comptant", "2-3 fois", "4-6 fois", "7-12 fois", "Plus de 12 fois"]
    e = q("""
        select p.tranche_echeances, count(*) nb, avg(p.montant_paye) moyen
        from marts.fct_order_payment p
        join marts.dim_date d on d.date_key = p.order_date_key
        where d.is_periode_analyse
        group by p.tranche_echeances
    """)
    e["rang"] = e.tranche_echeances.apply(lambda x: ordre.index(x) if x in ordre else 99)
    e = e.sort_values("rang")

    fig = go.Figure()
    fig.add_bar(x=e.tranche_echeances, y=e.nb, name="Nombre de paiements",
                marker_color=GRIS)
    fig.add_scatter(x=e.tranche_echeances, y=e.moyen, yaxis="y2",
                    name="Montant moyen", mode="lines+markers+text",
                    text=e.moyen.round(0).astype(int).astype(str) + " R$",
                    textposition="top center", textfont=dict(size=11, color=ORANGE),
                    line=dict(color=ORANGE, width=3.5))
    fig.update_layout(
        title="Plus le panier est eleve, plus le client fractionne son paiement",
        yaxis=dict(title="Paiements", **AXE),
        yaxis2=dict(title="Montant moyen (R$)", overlaying="y", side="right",
                    showgrid=False, range=[0, 480]),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
    )
    sauver(fig, "fig6_paiement")


if __name__ == "__main__":
    print("Generation des figures du rapport :")
    fig_croissance()
    fig_mom()
    fig_pareto()
    fig_logistique()
    fig_satisfaction()
    fig_paiement()
    print("Termine.")
