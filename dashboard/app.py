"""
Tableau de bord decisionnel Olist.

Couche de restitution du pipeline : interroge EXCLUSIVEMENT le schema `marts`
(le modele en etoile), jamais les couches raw ou staging. Un onglet par
question metier, avec des filtres globaux qui se propagent a tous les visuels.

Lancement : docker compose up -d dashboard  ->  http://localhost:8501
"""

import os
import warnings

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Olist - Tableau de bord decisionnel",
    layout="wide",
)

PALETTE = ["#2E5EAA", "#5B9BD5", "#F4A261", "#E76F51", "#2A9D8F", "#8D6E97", "#B0BEC5"]
VERT, ORANGE, ROUGE = "#2A9D8F", "#F4A261", "#E76F51"


# --------------------------------------------------------------------------- #
# Acces aux donnees
# --------------------------------------------------------------------------- #
@st.cache_resource
def get_engine():
    user = os.getenv("POSTGRES_USER", "dwh")
    pwd = os.getenv("POSTGRES_PASSWORD", "dwh")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "olist_dw")
    return create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}")


@st.cache_data(ttl=900, show_spinner=False)
def run(sql, params=None):
    raw = get_engine().raw_connection()
    try:
        return pd.read_sql(sql, raw, params=params or {})
    finally:
        raw.close()


@st.cache_data(ttl=3600, show_spinner=False)
def referentiels():
    bornes = run(
        "select min(date_day) d1, max(date_day) d2 from marts.dim_date "
        "where is_periode_analyse"
    ).iloc[0]
    regions = run(
        "select distinct region from marts.dim_customer "
        "where region <> 'Inconnu' order by 1"
    )["region"].tolist()
    segments = run("select distinct segment from marts.dim_product order by 1")[
        "segment"
    ].tolist()
    return bornes, regions, segments


# --------------------------------------------------------------------------- #
# Filtres globaux (se propagent a tous les onglets)
# --------------------------------------------------------------------------- #
bornes, REGIONS, SEGMENTS = referentiels()

st.sidebar.title("Filtres")
st.sidebar.caption("Ils s'appliquent a l'ensemble des onglets.")

periode = st.sidebar.date_input(
    "Periode d'achat",
    value=(bornes.d1, bornes.d2),
    min_value=bornes.d1,
    max_value=bornes.d2,
)
if isinstance(periode, tuple) and len(periode) == 2:
    d1, d2 = periode
else:
    d1, d2 = bornes.d1, bornes.d2

regions = st.sidebar.multiselect("Region du client", REGIONS, default=REGIONS)
segments = st.sidebar.multiselect("Segment produit", SEGMENTS, default=SEGMENTS)
ca_only = st.sidebar.checkbox(
    "Exclure les commandes annulees", value=True,
    help="Ne conserve que les statuts contribuant au chiffre d'affaires.",
)

P = {
    "d1": d1,
    "d2": d2,
    "regions": regions or REGIONS,
    "segments": segments or SEGMENTS,
}

# Fragments de clause WHERE reutilises par toutes les requetes
W_ITEM = """
    d.date_day between %(d1)s and %(d2)s
    and c.region = any(%(regions)s)
    and p.segment = any(%(segments)s)
"""
W_CA = " and s.is_chiffre_affaires" if ca_only else ""

JOINS = """
    from marts.fct_order_item f
    join marts.dim_date d          on d.date_key = f.order_date_key
    join marts.dim_customer c      on c.customer_key = f.customer_key
    join marts.dim_product p       on p.product_key = f.product_key
    join marts.dim_order_status s  on s.status_key = f.status_key
"""

st.sidebar.divider()
st.sidebar.caption(
    "Source : marts (modele en etoile).\n\n"
    "Projet 2 - M1 MBDA UFC/UNCHK 2026"
)

st.title("Olist - Tableau de bord decisionnel")
st.caption(
    f"Periode analysee : {d1:%d/%m/%Y} au {d2:%d/%m/%Y} | "
    f"{len(regions)} region(s) | {len(segments)} segment(s) produit"
)

# Garde-fou : une combinaison de filtres trop etroite viderait les requetes et
# ferait echouer les calculs (division par zero, idxmax sur table vide).
# On arrete proprement avec un message plutot que d'afficher une trace d'erreur.
_n = run(f"select count(*) n {JOINS} where {W_ITEM} {W_CA}", P).iloc[0].n
if _n == 0:
    st.warning(
        "Aucune donnee pour cette combinaison de filtres. "
        "Elargissez la periode, les regions ou les segments."
    )
    st.stop()

onglets = st.tabs([
    "Synthese",
    "1. Croissance",
    "2. Produits",
    "3. Logistique",
    "4. Satisfaction",
    "5. Clients",
])


# --------------------------------------------------------------------------- #
# Onglet 0 : synthese
# --------------------------------------------------------------------------- #
with onglets[0]:
    kpi = run(
        f"""
        select
            sum(f.montant_total)                                as ca,
            count(distinct f.order_id)                          as commandes,
            count(distinct f.customer_key)                      as clients,
            sum(f.montant_total)/count(distinct f.order_id)     as panier,
            avg(f.delai_livraison_jours)                        as delai,
            100.0*avg(f.is_retard::numeric)                     as retard
        {JOINS} where {W_ITEM} {W_CA}
        """,
        P,
    ).iloc[0]

    note = run(
        """
        select avg(note) n from marts.fct_order_review r
        join marts.dim_date d on d.date_key = r.order_date_key
        join marts.dim_customer c on c.customer_key = r.customer_key
        where d.date_day between %(d1)s and %(d2)s and c.region = any(%(regions)s)
        """,
        P,
    ).iloc[0].n

    c = st.columns(6)
    c[0].metric("Chiffre d'affaires", f"{kpi.ca/1e6:,.2f} M R$".replace(",", " "))
    c[1].metric("Commandes", f"{int(kpi.commandes):,}".replace(",", " "))
    c[2].metric("Clients", f"{int(kpi.clients):,}".replace(",", " "))
    c[3].metric("Panier moyen", f"{kpi.panier:,.2f} R$".replace(",", " "))
    c[4].metric("Delai moyen", f"{kpi.delai:.1f} j")
    c[5].metric("Note moyenne", f"{note:.2f} / 5")

    st.divider()

    eff = run(
        f"""
        select d.annee_mois, sum(f.montant_total) ca,
               count(distinct f.order_id) commandes
        {JOINS} where {W_ITEM} {W_CA}
        group by d.annee_mois order by d.annee_mois
        """,
        P,
    )

    fig = go.Figure()
    fig.add_bar(x=eff.annee_mois, y=eff.commandes, name="Commandes",
                marker_color="#C9D6E8", yaxis="y2")
    fig.add_scatter(x=eff.annee_mois, y=eff.ca, name="Chiffre d'affaires",
                    line=dict(color=PALETTE[0], width=3))
    fig.update_layout(
        title="Chiffre d'affaires et volume de commandes par mois",
        yaxis=dict(title="CA (R$)"),
        yaxis2=dict(title="Commandes", overlaying="y", side="right", showgrid=False),
        hovermode="x unified", height=420, legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        reg = run(
            f"""
            select c.region, sum(f.montant_total) ca
            {JOINS} where {W_ITEM} {W_CA}
            group by c.region order by ca desc
            """,
            P,
        )
        st.plotly_chart(
            px.pie(reg, names="region", values="ca", hole=0.45,
                   color_discrete_sequence=PALETTE,
                   title="Repartition du CA par region"),
            use_container_width=True,
        )
    with g2:
        seg = run(
            f"""
            select p.segment, sum(f.montant_total) ca
            {JOINS} where {W_ITEM} {W_CA}
            group by p.segment order by ca desc
            """,
            P,
        )
        st.plotly_chart(
            px.bar(seg, x="ca", y="segment", orientation="h",
                   color_discrete_sequence=[PALETTE[0]],
                   title="CA par segment produit").update_layout(
                       yaxis=dict(categoryorder="total ascending")),
            use_container_width=True,
        )


# --------------------------------------------------------------------------- #
# Onglet 1 : croissance  (question metier 1)
# --------------------------------------------------------------------------- #
with onglets[1]:
    st.subheader("Comment evolue le chiffre d'affaires et a quel rythme ?")

    m = run(
        f"""
        with base as (
            select d.annee_mois, d.annee,
                   sum(f.montant_total) ca,
                   count(distinct f.order_id) commandes
            {JOINS} where {W_ITEM} {W_CA}
            group by d.annee_mois, d.annee
        )
        select annee_mois, annee, ca, commandes,
               ca/nullif(commandes,0) panier,
               100.0*(ca - lag(ca) over (order by annee_mois))
                   / nullif(lag(ca) over (order by annee_mois),0) mom,
               100.0*(ca - lag(ca,12) over (order by annee_mois))
                   / nullif(lag(ca,12) over (order by annee_mois),0) yoy
        from base order by annee_mois
        """,
        P,
    )

    k = st.columns(3)
    k[0].metric("Croissance MoM moyenne", f"{m.mom.mean():.1f} %")
    if m.yoy.notna().any():
        k[1].metric("Croissance YoY (dernier mois)", f"{m.yoy.dropna().iloc[-1]:.0f} %")
    k[2].metric("Meilleur mois", f"{m.loc[m.ca.idxmax(), 'annee_mois']}")

    couleurs = [VERT if v >= 0 else ROUGE for v in m.mom.fillna(0)]
    fig = go.Figure()
    fig.add_bar(x=m.annee_mois, y=m.mom, marker_color=couleurs, name="MoM %")
    fig.update_layout(title="Croissance mois sur mois (%)", height=340,
                      yaxis_title="%", hovermode="x")
    st.plotly_chart(fig, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(
            px.line(m, x="annee_mois", y="panier", markers=True,
                    color_discrete_sequence=[PALETTE[2]],
                    title="Panier moyen (R$) - stable = croissance par le volume"),
            use_container_width=True,
        )
    with g2:
        trim = run(
            f"""
            select d.annee_trimestre, c.region, sum(f.montant_total) ca
            {JOINS} where {W_ITEM} {W_CA}
            group by d.annee_trimestre, c.region order by d.annee_trimestre
            """,
            P,
        )
        st.plotly_chart(
            px.bar(trim, x="annee_trimestre", y="ca", color="region",
                   color_discrete_sequence=PALETTE,
                   title="CA par trimestre et region"),
            use_container_width=True,
        )

    st.dataframe(
        m.assign(
            ca=m.ca.round(0), panier=m.panier.round(2),
            mom=m.mom.round(1), yoy=m.yoy.round(1),
        ).rename(columns={
            "annee_mois": "Mois", "ca": "CA (R$)", "commandes": "Commandes",
            "panier": "Panier moyen", "mom": "MoM %", "yoy": "YoY %",
        }).drop(columns=["annee"]),
        use_container_width=True, hide_index=True,
    )


# --------------------------------------------------------------------------- #
# Onglet 2 : produits  (question metier 2 - Pareto)
# --------------------------------------------------------------------------- #
with onglets[2]:
    st.subheader("Quelles categories concentrent le chiffre d'affaires ?")

    pareto = run(
        f"""
        with base as (
            select p.segment, p.categorie,
                   sum(f.montant_total) ca,
                   sum(f.frais_port) transport,
                   count(*) articles
            {JOINS} where {W_ITEM} {W_CA}
            group by p.segment, p.categorie
        )
        select *,
               row_number() over (order by ca desc) rang,
               100.0*ca/sum(ca) over () part,
               100.0*sum(ca) over (order by ca desc rows unbounded preceding)
                   / sum(ca) over () cumul,
               100.0*transport/nullif(ca,0) poids_transport
        from base order by ca desc
        """,
        P,
    )

    n80 = int((pareto.cumul <= 80).sum())
    k = st.columns(3)
    k[0].metric("Categories actives", len(pareto))
    k[1].metric("Categories pour 80 % du CA", n80)
    k[2].metric("Concentration", f"{100*n80/len(pareto):.0f} % du catalogue")

    top = pareto.head(20)
    fig = go.Figure()
    fig.add_bar(x=top.categorie, y=top.ca, name="CA", marker_color=PALETTE[0])
    fig.add_scatter(x=top.categorie, y=top.cumul, name="Cumul %",
                    yaxis="y2", line=dict(color=ORANGE, width=3))
    fig.add_hline(y=80, line_dash="dot", line_color=ROUGE, yref="y2")
    fig.update_layout(
        title="Courbe de Pareto - 20 premieres categories",
        yaxis=dict(title="CA (R$)"),
        yaxis2=dict(title="Cumul (%)", overlaying="y", side="right",
                    range=[0, 105], showgrid=False),
        height=460, hovermode="x unified", legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(
            px.treemap(pareto, path=["segment", "categorie"], values="ca",
                       color_discrete_sequence=PALETTE,
                       title="Structure du catalogue (segment > categorie)"),
            use_container_width=True,
        )
    with g2:
        t = pareto.nlargest(15, "ca")
        st.plotly_chart(
            px.bar(t, x="poids_transport", y="categorie", orientation="h",
                   color="poids_transport", color_continuous_scale="RdYlGn_r",
                   title="Poids du transport dans le CA (%) - levier de marge"
                   ).update_layout(yaxis=dict(categoryorder="total ascending")),
            use_container_width=True,
        )


# --------------------------------------------------------------------------- #
# Onglet 3 : logistique  (question metier 3)
# --------------------------------------------------------------------------- #
with onglets[3]:
    st.subheader("Delais de livraison et respect de la promesse client")

    logi = run(
        f"""
        select c.region, c.etat, c.etat_code,
               count(distinct f.order_id) commandes,
               avg(f.delai_livraison_jours) delai,
               avg(f.delai_estime_jours) promis,
               avg(f.ecart_promesse_jours) ecart,
               100.0*avg(f.is_retard::numeric) retard
        {JOINS} where {W_ITEM} and s.is_livree
        group by c.region, c.etat, c.etat_code
        having count(distinct f.order_id) >= 30
        order by delai desc
        """,
        P,
    )

    # Le seuil de significativite (>= 30 commandes) peut vider la table sur un
    # filtre etroit : on le signale au lieu de laisser planter les indicateurs.
    if logi.empty:
        st.info(
            "Aucun etat n'atteint le seuil de 30 commandes livrees sur ce "
            "perimetre. Elargissez la periode ou les regions."
        )
        st.stop()

    k = st.columns(4)
    # Moyenne PONDEREE par le volume de commandes : la moyenne des moyennes
    # par etat surponderait les petits etats et contredirait le KPI de synthese.
    delai_national = (logi.delai * logi.commandes).sum() / logi.commandes.sum()
    k[0].metric("Delai moyen national", f"{delai_national:.1f} j")
    k[1].metric("Etat le plus rapide",
                f"{logi.iloc[-1].etat} ({logi.iloc[-1].delai:.1f} j)")
    k[2].metric("Etat le plus lent",
                f"{logi.iloc[0].etat} ({logi.iloc[0].delai:.1f} j)")
    k[3].metric("Pire taux de retard",
                f"{logi.loc[logi.retard.idxmax(), 'etat_code']} "
                f"({logi.retard.max():.1f} %)")

    st.info(
        "Lecture cle : les etats les plus LENTS ne sont pas les plus EN RETARD. "
        "Le Norte livre en 26-28 jours mais tient sa promesse car la date estimee "
        "y est tres prudente. Le probleme n'est pas la vitesse de livraison mais "
        "la calibration de la promesse client.",
    )

    fig = px.scatter(
        logi, x="delai", y="retard", size="commandes", color="region",
        hover_name="etat", color_discrete_sequence=PALETTE,
        labels={"delai": "Delai moyen (jours)", "retard": "Taux de retard (%)"},
        title="Vitesse de livraison vs respect de la promesse",
    )
    fig.update_layout(height=440)
    st.plotly_chart(fig, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        d = logi.sort_values("delai")
        st.plotly_chart(
            px.bar(d, x="delai", y="etat", orientation="h", color="region",
                   color_discrete_sequence=PALETTE,
                   title="Delai moyen de livraison par etat (jours)"),
            use_container_width=True,
        )
    with g2:
        r = logi.sort_values("retard")
        st.plotly_chart(
            px.bar(r, x="retard", y="etat", orientation="h", color="retard",
                   color_continuous_scale="RdYlGn_r",
                   title="Taux de commandes en retard par etat (%)"),
            use_container_width=True,
        )


# --------------------------------------------------------------------------- #
# Onglet 4 : satisfaction  (question metier 4)
# --------------------------------------------------------------------------- #
with onglets[4]:
    st.subheader("Quel est l'impact du retard de livraison sur la note client ?")

    ORDRE = ["tres en avance", "en avance", "a l heure", "retard leger",
             "retard moyen", "retard important", "non livre"]

    sat = run(
        """
        select r.tranche_retard, count(*) avis, avg(r.note) note,
               100.0*avg(r.is_satisfait::int::numeric) satisfaits,
               100.0*avg(r.is_insatisfait::int::numeric) insatisfaits
        from marts.fct_order_review r
        join marts.dim_date d     on d.date_key = r.order_date_key
        join marts.dim_customer c on c.customer_key = r.customer_key
        where d.date_day between %(d1)s and %(d2)s and c.region = any(%(regions)s)
        group by r.tranche_retard
        """,
        P,
    )
    sat["ordre"] = sat.tranche_retard.apply(
        lambda x: ORDRE.index(x) if x in ORDRE else 99)
    sat = sat.sort_values("ordre")

    k = st.columns(3)
    k[0].metric("Note moyenne globale",
                f"{(sat.note*sat.avis).sum()/sat.avis.sum():.2f} / 5")
    a_l_heure = sat[sat.tranche_retard == "a l heure"]
    moyen = sat[sat.tranche_retard == "retard moyen"]
    if not a_l_heure.empty and not moyen.empty:
        k[1].metric("Chute de note au-dela de 3 j de retard",
                    f"{moyen.note.iloc[0] - a_l_heure.note.iloc[0]:.2f} pt")
        k[2].metric("Insatisfaction au-dela de 3 j",
                    f"{moyen.insatisfaits.iloc[0]:.0f} %",
                    delta=f"{moyen.insatisfaits.iloc[0]-a_l_heure.insatisfaits.iloc[0]:.0f} pts",
                    delta_color="inverse")

    couleurs = [VERT if n >= 4 else (ORANGE if n >= 3 else ROUGE) for n in sat.note]
    fig = go.Figure()
    fig.add_bar(x=sat.tranche_retard, y=sat.note, marker_color=couleurs,
                text=sat.note.round(2), textposition="outside")
    fig.add_hline(y=3, line_dash="dot", line_color="#888")
    fig.update_layout(
        title="Note moyenne selon le retard de livraison - effet de seuil a 3 jours",
        yaxis=dict(title="Note / 5", range=[0, 5]), height=430,
    )
    st.plotly_chart(fig, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        emp = sat.melt(id_vars="tranche_retard",
                       value_vars=["satisfaits", "insatisfaits"],
                       var_name="type", value_name="pct")
        st.plotly_chart(
            px.bar(emp, x="tranche_retard", y="pct", color="type", barmode="group",
                   color_discrete_map={"satisfaits": VERT, "insatisfaits": ROUGE},
                   title="Satisfaits (note >= 4) vs insatisfaits (note <= 2)"),
            use_container_width=True,
        )
    with g2:
        st.plotly_chart(
            px.bar(sat, x="tranche_retard", y="avis",
                   color_discrete_sequence=[PALETTE[1]],
                   title="Volume d'avis par tranche de retard"),
            use_container_width=True,
        )


# --------------------------------------------------------------------------- #
# Onglet 5 : clients  (question metier 5)
# --------------------------------------------------------------------------- #
with onglets[5]:
    st.subheader("Moyens de paiement, fractionnement et fidelite")

    pay = run(
        """
        select p.libelle_paiement, p.tranche_echeances,
               count(*) nb, sum(p.montant_paye) montant,
               avg(p.montant_paye) moyen
        from marts.fct_order_payment p
        join marts.dim_date d     on d.date_key = p.order_date_key
        join marts.dim_customer c on c.customer_key = p.customer_key
        where d.date_day between %(d1)s and %(d2)s and c.region = any(%(regions)s)
        group by p.libelle_paiement, p.tranche_echeances
        """,
        P,
    )

    fid = run(
        """
        select segment_fidelite, count(*) clients
        from marts.dim_customer where region = any(%(regions)s)
        group by segment_fidelite
        """,
        P,
    )
    recurrents = 100 * (1 - fid.loc[fid.segment_fidelite.str.startswith("Unique"),
                                    "clients"].sum() / fid.clients.sum())

    ORDRE_E = ["Comptant", "2-3 fois", "4-6 fois", "7-12 fois", "Plus de 12 fois"]
    ech = pay.groupby("tranche_echeances", as_index=False).agg(
        nb=("nb", "sum"), moyen=("moyen", "mean"))
    ech["ordre"] = ech.tranche_echeances.apply(
        lambda x: ORDRE_E.index(x) if x in ORDRE_E else 99)
    ech = ech.sort_values("ordre")
    part_fractionne = 100 * ech[ech.tranche_echeances != "Comptant"].nb.sum() / ech.nb.sum()

    k = st.columns(3)
    k[0].metric("Clients recurrents", f"{recurrents:.1f} %")
    k[1].metric("Paiements fractionnes", f"{part_fractionne:.1f} %")
    k[2].metric("Panier moyen en 7-12 fois",
                f"{ech[ech.tranche_echeances=='7-12 fois'].moyen.mean():.0f} R$")

    st.warning(
        f"Point de vigilance strategique : {100-recurrents:.1f} % des clients "
        "n'achetent qu'une seule fois. La croissance repose integralement sur "
        "l'acquisition, jamais sur la retention.",
    )

    g1, g2 = st.columns(2)
    with g1:
        moy = pay.groupby("libelle_paiement", as_index=False).montant.sum()
        st.plotly_chart(
            px.pie(moy, names="libelle_paiement", values="montant", hole=0.45,
                   color_discrete_sequence=PALETTE,
                   title="Repartition du montant par moyen de paiement"),
            use_container_width=True,
        )
    with g2:
        st.plotly_chart(
            px.pie(fid, names="segment_fidelite", values="clients", hole=0.45,
                   color_discrete_sequence=[PALETTE[6], PALETTE[2], PALETTE[4]],
                   title="Segmentation des clients par fidelite"),
            use_container_width=True,
        )

    fig = go.Figure()
    fig.add_bar(x=ech.tranche_echeances, y=ech.nb, name="Nombre de paiements",
                marker_color=PALETTE[1])
    fig.add_scatter(x=ech.tranche_echeances, y=ech.moyen, name="Montant moyen (R$)",
                    yaxis="y2", line=dict(color=ORANGE, width=3), mode="lines+markers")
    fig.update_layout(
        title="Fractionnement du paiement : plus le panier est eleve, "
              "plus le client echelonne",
        yaxis=dict(title="Paiements"),
        yaxis2=dict(title="Montant moyen (R$)", overlaying="y", side="right",
                    showgrid=False),
        height=420, hovermode="x unified", legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig, use_container_width=True)
