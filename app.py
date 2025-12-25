import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv
import os
from datetime import datetime

# =======================
# CONFIG
# =======================
QUESTIONS_FILE = "questions_ici.xlsx"
INVITES_FILE = "invites.csv"
RESULTATS_FILE = "resultats_innovation.csv"

st.set_page_config(
    page_title="Indice de Culture de l’Innovation – ICI",
    layout="centered"
)

# =======================
# UTILS
# =======================
def safe_read_csv(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)

def get_maturity_level(score, df_interp):
    for _, row in df_interp.iterrows():
        if row["min"] <= score <= row["max"]:
            return row["niveau"], row["description"]
    return "Inconnu", ""

# =======================
# LOAD QUESTIONS
# =======================
try:
    df_q = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
    df_interp = pd.read_excel(QUESTIONS_FILE, sheet_name="interpretation")
except Exception as e:
    st.error("❌ Erreur chargement questions_ici.xlsx")
    st.stop()

required_cols = {"axe", "code", "question"}
if not required_cols.issubset(df_q.columns):
    st.error("❌ Colonnes manquantes dans l’onglet questions")
    st.stop()

axes_data = {
    axe: df_q[df_q["axe"] == axe]["code"].tolist()
    for axe in df_q["axe"].unique()
}

questions_sequence = df_q.to_dict("records")

# =======================
# SESSION
# =======================
if "step" not in st.session_state:
    st.session_state.step = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "q_index" not in st.session_state:
    st.session_state.q_index = 0

# =======================
# STEP 0 – AUTH
# =======================
if st.session_state.step == 0:
    st.title("🔐 Accès au diagnostic ICI")

    email = st.text_input("Email")
    code = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        df_inv = pd.read_csv(INVITES_FILE)
        user = df_inv[(df_inv.email.str.lower() == email.lower()) & (df_inv.code == code)]

        if user.empty:
            st.error("Accès refusé")
        else:
            user = user.iloc[0]
            st.session_state.user = user

            if user.admin == "OUI":
                st.info("Accès administrateur")
                st.session_state.step = 99
            else:
                st.session_state.step = 1
            st.rerun()

# =======================
# STEP 1 – QUESTIONNAIRE
# =======================
elif st.session_state.step == 1:
    q = questions_sequence[st.session_state.q_index]
    st.subheader(q["axe"])
    st.write(q["question"])

    st.session_state.responses[q["code"]] = st.select_slider(
        "Votre réponse",
        [1, 2, 3, 4, 5],
        format_func=lambda x: [
            "Pas du tout d’accord",
            "Pas d’accord",
            "Neutre",
            "D’accord",
            "Tout à fait"
        ][x - 1],
        key=q["code"]
    )

    st.progress((st.session_state.q_index + 1) / len(questions_sequence))

    if st.button("Suivant"):
        if st.session_state.q_index < len(questions_sequence) - 1:
            st.session_state.q_index += 1
        else:
            st.session_state.step = 2
        st.rerun()

# =======================
# STEP 2 – RESULTATS USER
# =======================
elif st.session_state.step == 2:
    r = st.session_state.responses

    scores_axes = {
        axe: sum(r[q] for q in qs) / len(qs)
        for axe, qs in axes_data.items()
    }

    ici = round(sum(scores_axes.values()) / len(scores_axes) * 20, 1)
    niveau, desc = get_maturity_level(ici, df_interp)

    df_out = pd.DataFrame([{
        "email": st.session_state.user.email,
        "filiale": st.session_state.user.filiale,
        **r,
        **scores_axes,
        "ICI": ici,
        "niveau": niveau,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    }])

    if os.path.exists(RESULTATS_FILE) and os.stat(RESULTATS_FILE).st_size > 0:
        df_out.to_csv(RESULTATS_FILE, mode="a", header=False, index=False)
    else:
        df_out.to_csv(RESULTATS_FILE, index=False)

    st.success(f"Score ICI : {ici}/100 – {niveau}")
    st.info(desc)

    fig = go.Figure(go.Scatterpolar(
        r=list(scores_axes.values()) + [list(scores_axes.values())[0]],
        theta=list(scores_axes.keys()) + [list(scores_axes.keys())[0]],
        fill="toself"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5])))
    st.plotly_chart(fig)

    if st.button("⬅ Retour à l’accueil"):
        st.session_state.step = 0
        st.session_state.responses = {}
        st.session_state.q_index = 0
        st.rerun()

# =======================
# STEP 99 – DASHBOARD ADMIN
# =======================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Administrateur – ICI")

    df_inv = pd.read_csv(INVITES_FILE)
    df_res = safe_read_csv(RESULTATS_FILE)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Invités", len(df_inv))
    col2.metric("Réponses", len(df_res))
    col3.metric("Filiales", df_inv.filiale.nunique())
    col4.metric("Score moyen", f"{df_res.ICI.mean():.1f}" if not df_res.empty else "—")

    if not df_res.empty:
        st.subheader("📈 ICI par filiale")
        fig = px.bar(
            df_res.groupby("filiale")["ICI"].mean().reset_index(),
            x="filiale", y="ICI"
        )
        st.plotly_chart(fig)

        st.subheader("📊 Répartition maturité")
        fig2 = px.histogram(df_res, x="niveau")
        st.plotly_chart(fig2)

    st.subheader("📋 Détails réponses")
    st.dataframe(df_res, use_container_width=True)

    st.download_button(
        "⬇ Export résultats",
        df_res.to_csv(index=False),
        "resultats_ici.csv"
    )

    if st.button("⬅ Retour authentification"):
        st.session_state.step = 0
        st.rerun()
