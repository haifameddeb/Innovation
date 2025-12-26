import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from io import BytesIO
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
    df_interp = pd.read_excel(QUESTIONS_FILE, sheet_name="interpretation")
except Exception:
    st.error("❌ Impossible de charger questions_ici.xlsx")
    st.stop()

df_q = clean_columns(df_q)
df_interp = clean_columns(df_interp)

if "id" in df_q.columns and "code" not in df_q.columns:
    df_q = df_q.rename(columns={"id": "code"})

required_cols = {"axe", "code", "question"}
if not required_cols.issubset(df_q.columns):
    st.error("❌ Colonnes manquantes dans l’onglet questions")
    st.stop()

questions_sequence = df_q.to_dict("records")

axes_data = {
    axe: df_q[df_q["axe"] == axe]["code"].tolist()
    for axe in df_q["axe"].unique()
}

def get_maturity_level(score):
    for _, row in df_interp.iterrows():
        if row["min"] <= score <= row["max"]:
            return row["niveau"]
    return "Inconnu"

# =======================
# SESSION INIT
# =======================
if "step" not in st.session_state:
    st.session_state.step = 0
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}

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
            st.session_state.user = user

            # 🔥 INITIALISATION CRITIQUE
            st.session_state.q_index = 0
            st.session_state.responses = {}

            admin_flag = str(user.get("admin", "")).strip().lower()

            if admin_flag == "oui":
                st.session_state.step = 99
            else:
                st.session_state.step = 1

            st.rerun()

# =======================
# STEP 1 – QUESTIONNAIRE
# =======================
elif st.session_state.step == 1:

    if st.session_state.q_index >= len(questions_sequence):
        st.session_state.step = 2
        st.rerun()

    q = questions_sequence[st.session_state.q_index]

    st.subheader(f"Axe : {q['axe']}")
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
        st.session_state.q_index += 1
        st.rerun()

# =======================
# STEP 2 – ENREGISTREMENT
# =======================
elif st.session_state.step == 2:

    r = st.session_state.responses

    scores_axes = {
        axe: sum(r[q] for q in qs) / len(qs)
        for axe, qs in axes_data.items()
    }

    ici = round(sum(scores_axes.values()) / len(scores_axes) * 20, 1)
    niveau = get_maturity_level(ici)

    df_out = pd.DataFrame([{
        "email": st.session_state.user["email"],
        "filiale": st.session_state.user["filiale"],
        **r,
        **scores_axes,
        "ici": ici,
        "niveau": niveau,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    }])

    if os.path.exists(RESULTATS_FILE):
        df_out.to_csv(RESULTATS_FILE, mode="a", header=False, index=False, sep=";")
    else:
        df_out.to_csv(RESULTATS_FILE, index=False, sep=";")

    st.success(f"Merci pour votre participation 🙏 – Score ICI : {ici}/100")

    if st.button("⬅ Retour accueil"):
        st.session_state.step = 0
        st.rerun()

# =======================
# STEP 99 – DASHBOARD ADMIN
# =======================
elif st.session_state.step == 99:

    st.title("📊 Dashboard Administrateur – ICI")

    df_inv = clean_columns(pd.read_csv(INVITES_FILE))
    df_res = safe_read_csv(RESULTATS_FILE)
    if not df_res.empty:
        df_res = clean_columns(df_res)

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Invités", len(df_inv))
    col2.metric("📝 Réponses", len(df_res))
    col3.metric("🏢 Filiales", df_inv["filiale"].nunique())

    score_moyen = "—"
    if not df_res.empty and "ici" in df_res.columns:
        score_moyen = f"{df_res['ici'].astype(float).mean():.1f}"

    col4.metric("📊 Score moyen ICI", score_moyen)

    # ICI moyen par filiale
    if not df_res.empty:
        st.subheader("📈 ICI moyen par filiale")
        df_plot = df_res.copy()
        df_plot["ici"] = pd.to_numeric(df_plot["ici"], errors="coerce")

        fig = px.bar(
            df_plot.groupby("filiale", as_index=False)["ici"].mean(),
            x="filiale",
            y="ici",
            text_auto=".1f"
        )
        fig.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)

    # Suivi des invités
    st.subheader("📋 Suivi des invitations")

    df_res_light = pd.DataFrame()
    if not df_res.empty:
        df_res_light = df_res[["email", "date"]].drop_duplicates()

    df_suivi = df_inv.merge(df_res_light, on="email", how="left")

    df_suivi["invité"] = "✅"
    df_suivi["a répondu"] = df_suivi["date"].notna().map({True: "✅", False: "❌"})
    df_suivi["date de réponse"] = df_suivi["date"].fillna("—")

    df_display = df_suivi[
        ["email", "filiale", "invité", "a répondu", "date de réponse"]
    ]

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Relance
    df_non_rep = df_display[df_display["a répondu"] == "❌"]
    if not df_non_rep.empty:
        st.download_button(
            "🔔 Export relance non-répondants",
            df_non_rep["email"].to_csv(index=False),
            "relance_non_repondants.csv"
        )

    # Export Excel
    output = BytesIO()
    df_display.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    st.download_button(
        "📤 Export Excel – Suivi participation",
        data=output,
        file_name="suivi_participation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("⬅ Déconnexion"):
        st.session_state.step = 0
        st.rerun()
