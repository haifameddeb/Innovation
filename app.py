import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from pandas.errors import EmptyDataError, ParserError

# =======================
# CONFIG
# =======================
QUESTIONS_FILE = "questions_ici.xlsx"
INVITES_FILE = "invites.csv"
RESULTATS_FILE = "resultats_innovation.csv"

st.set_page_config(
    page_title="Indice de Culture de l’Innovation – ICI",
    layout="wide"
)

# =======================
# UTILS
# =======================
def clean_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def safe_read_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, sep=";", engine="python")
        df = df.loc[:, ~df.columns.str.match(r"^unnamed")]
        return df
    except (EmptyDataError, ParserError):
        return pd.DataFrame()

# =======================
# LOAD QUESTIONS
# =======================
try:
    df_q = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
except Exception:
    st.error("❌ Impossible de charger questions_ici.xlsx")
    st.stop()

df_q = clean_columns(df_q)

if "id" in df_q.columns and "code" not in df_q.columns:
    df_q = df_q.rename(columns={"id": "code"})

# =======================
# SESSION
# =======================
if "step" not in st.session_state:
    st.session_state.step = 0

# =======================
# STEP 0 – AUTH
# =======================
if st.session_state.step == 0:
    st.title("🔐 Accès au diagnostic ICI")

    email = st.text_input("Email")
    code = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        df_inv = clean_columns(pd.read_csv(INVITES_FILE))

        user = df_inv[
            (df_inv["email"].str.lower() == email.lower()) &
            (df_inv["code"] == code)
        ]

        if user.empty:
            st.error("Accès refusé")
        else:
            user = user.iloc[0]
            admin_flag = str(user.get("admin", "")).strip().lower()

            if admin_flag == "oui":
                st.session_state.step = 99
            else:
                st.session_state.step = 1
            st.rerun()




# =======================
# STEP 99 – DASHBOARD ADMIN
# =======================
elif st.session_state.step == 99:

    st.title("📊 Dashboard Administrateur – ICI")

    # =======================
    # DATA
    # =======================
    df_inv = clean_columns(pd.read_csv(INVITES_FILE))
    df_res = safe_read_csv(RESULTATS_FILE)
    if not df_res.empty:
        df_res = clean_columns(df_res)

    # =======================
    # KPI
    # =======================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Invités", len(df_inv))
    col2.metric("📝 Réponses", len(df_res))
    col3.metric("🏢 Filiales", df_inv["filiale"].nunique())

    score_moyen = "—"
    if not df_res.empty and "ici" in df_res.columns:
        score_moyen = f"{df_res['ici'].astype(float).mean():.1f}"

    col4.metric("📊 Score moyen ICI", score_moyen)

    # =======================
    # VUE PAR FILIALE
    # =======================
    st.subheader("🟣 Vue par filiale / direction")

    filiales = sorted(df_inv["filiale"].unique())
    filiale_sel = st.multiselect(
        "Filiale",
        filiales,
        default=filiales
    )

    df_inv_f = df_inv[df_inv["filiale"].isin(filiale_sel)]
    df_res_f = df_res[df_res["filiale"].isin(filiale_sel)] if not df_res.empty else df_res

    # =======================
    # TEMPS MOYEN DE RÉPONSE
    # =======================
    temps_moyen = "—"
    if not df_res_f.empty and "date" in df_res_f.columns:
        df_res_f["date"] = pd.to_datetime(df_res_f["date"], errors="coerce")
        df_first = df_res_f.groupby("email")["date"].min()
        temps_moyen = f"{df_first.diff().mean().total_seconds() / 3600:.1f} h"

    st.metric("🕒 Temps moyen de réponse", temps_moyen)

    # =======================
    # ICI MOYEN PAR FILIALE
    # =======================
    if not df_res_f.empty and "ici" in df_res_f.columns:
        st.subheader("📈 ICI moyen par filiale")
        fig = px.bar(
            df_res_f.groupby("filiale")["ici"].mean().reset_index(),
            x="filiale",
            y="ici",
            labels={"ici": "Score ICI"}
        )
        st.plotly_chart(fig, use_container_width=True)

    # =======================
    # SUIVI DES INVITÉS
    # =======================
    st.subheader("📋 Suivi des invitations")

    df_res_light = pd.DataFrame()
    if not df_res_f.empty:
        df_res_light = df_res_f[["email", "date"]].drop_duplicates()

    df_suivi = df_inv_f.merge(
        df_res_light,
        on="email",
        how="left"
    )

    df_suivi["invité"] = "✅"
    df_suivi["a répondu"] = df_suivi["date"].notna().map({True: "✅", False: "❌"})
    df_suivi["date de réponse"] = df_suivi["date"].fillna("—")

    df_display = df_suivi[
        ["email", "filiale", "invité", "a répondu", "date de réponse"]
    ]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

    # =======================
    # RELANCE NON-RÉPONDANTS
    # =======================
    st.subheader("🔔 Relancer les non-répondants")

    df_non_rep = df_display[df_display["a répondu"] == "❌"]

    if df_non_rep.empty:
        st.success("Tous les invités ont répondu 🎉")
    else:
        st.warning(f"{len(df_non_rep)} invité(s) à relancer")

        st.download_button(
            "📤 Export liste de relance (emails)",
            df_non_rep["email"].to_csv(index=False),
            "relance_non_repondants.csv"
        )

    # =======================
    # EXPORT EXCEL SUIVI
    # =======================
    st.subheader("📤 Export")

    st.download_button(
        "⬇ Export Excel – Suivi participation",
        df_display.to_excel(index=False, engine="openpyxl"),
        "suivi_participation.xlsx"
    )

    # =======================
    # LOGOUT
    # =======================
    if st.button("⬅ Déconnexion"):
        st.session_state.step = 0
        st.rerun()

