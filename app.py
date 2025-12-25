import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv, os
from datetime import datetime

# =============================
# CONFIG
# =============================
INVITES_FILE = "invites.csv"
RESULTATS_FILE = "resultats_innovation.csv"
QUESTIONS_FILE = "questions_ici.xlsx"

st.set_page_config(page_title="ICI – Dashboard", layout="wide")

# =============================
# LOAD QUESTIONS & RULES
# =============================
df_q = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
df_interp = pd.read_excel(QUESTIONS_FILE, sheet_name="interpretation")

axes = df_q["axe"].unique().tolist()

# =============================
# SESSION
# =============================
if "step" not in st.session_state:
    st.session_state.step = 0

# =============================
# HELPERS
# =============================
def niveau_maturite(score):
    row = df_interp[
        (df_interp.min <= score) & (df_interp.max >= score)
    ]
    return row.iloc[0]["niveau"] if not row.empty else "Non défini"

# =============================
# AUTHENTIFICATION
# =============================
if st.session_state.step == 0:
    st.title("🔐 Accès Diagnostic ICI")

    email = st.text_input("Email")
    code = st.text_input("Code", type="password")

    if st.button("Accéder"):
        df_inv = pd.read_csv(INVITES_FILE)
        user = df_inv[
            (df_inv.email.str.lower() == email.lower()) &
            (df_inv.code == code)
        ]

        if user.empty:
            st.error("Accès refusé")
        else:
            st.session_state.user = user.iloc[0].to_dict()
            if user.iloc[0]["admin"] == "OUI":
                st.session_state.step = 99
            else:
                st.session_state.step = 1
            st.rerun()

# =============================
# DASHBOARD ADMIN
# =============================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Administrateur – ICI")

    df_inv = pd.read_csv(INVITES_FILE)

    if os.path.exists(RESULTATS_FILE) and os.path.getsize(RESULTATS_FILE) > 0:
        df_res = pd.read_csv(RESULTATS_FILE)
    else:
        st.warning("Aucune réponse enregistrée")
        df_res = pd.DataFrame()

    # =============================
    # KPI GLOBAUX
    # =============================
    col1, col2, col3, col4, col5 = st.columns(5)

    total_inv = len(df_inv)
    total_rep = len(df_inv[df_inv.statut == "OUI"])
    taux = round((total_rep / total_inv) * 100, 1) if total_inv else 0

    ici_moy = round(df_res["ICI"].mean(), 1) if not df_res.empty else 0
    niveau = niveau_maturite(ici_moy)

    col1.metric("ICI moyen Groupe", ici_moy)
    col2.metric("Niveau de maturité", niveau)
    col3.metric("Taux participation", f"{taux}%")
    col4.metric("Répondants", total_rep)
    col5.metric("Filiales", df_inv.filiale.nunique())

    st.divider()

    # =============================
    # KPI PAR FILIALE
    # =============================
    st.subheader("🏢 KPI par filiale")

    if not df_res.empty:
        df_merge = df_res.merge(
            df_inv[["email", "filiale"]],
            on="email",
            how="left"
        )

        kpi_filiale = (
            df_merge.groupby("filiale")
            .agg(
                ICI_moyen=("ICI", "mean"),
                Réponses=("email", "count")
            )
            .reset_index()
        )

        invites_fil = (
            df_inv.groupby("filiale")
            .size()
            .reset_index(name="Invités")
        )

        kpi = kpi_filiale.merge(invites_fil, on="filiale")
        kpi["Taux %"] = round((kpi["Réponses"] / kpi["Invités"]) * 100, 1)
        kpi["Maturité"] = kpi["ICI_moyen"].apply(niveau_maturite)

        st.dataframe(kpi, use_container_width=True)

        # =============================
        # GRAPHIQUES
        # =============================
        fig = px.bar(
            kpi,
            x="filiale",
            y="ICI_moyen",
            color="Maturité",
            title="Indice ICI moyen par filiale"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    if st.button("⬅️ Retour accueil"):
        st.session_state.step = 0
        st.rerun()
