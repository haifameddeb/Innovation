import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================
# CONFIG
# =========================
QUESTIONS_FILE = "questions_ici.xlsx"
RESULTATS_FILE = "resultats_innovation.csv"
INVITES_FILE = "invites.csv"

# =========================
# UTILS
# =========================
def clean_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def load_questions():
    df_q = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
    df_q = clean_columns(df_q)

    required = {"axe", "code", "question"}
    if not required.issubset(df_q.columns):
        st.error("❌ Colonnes manquantes dans l’onglet questions.")
        st.stop()

    return df_q

def check_invitation(email):
    if not os.path.exists(INVITES_FILE):
        st.error("❌ Fichier des invités introuvable.")
        st.stop()

    df_inv = pd.read_csv(INVITES_FILE, sep=";")
    df_inv = clean_columns(df_inv)

    return email.lower() in df_inv["email"].str.lower().values

# =========================
# PAGE QUESTIONNAIRE
# =========================
def page_questionnaire():

    # =========================
    # SÉCURITÉ D’ACCÈS
    # =========================
    if "user" not in st.session_state:
        st.error("Accès non autorisé.")
        st.stop()

    email_user = st.session_state.user["email"]

    if not check_invitation(email_user):
        st.error("❌ Votre adresse email n’est pas autorisée à accéder au questionnaire.")
        st.stop()

    # =========================
    # INIT SESSION
    # =========================
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    # =========================
    # LOAD QUESTIONS
    # =========================
    df_q = load_questions()
    questions = df_q.to_dict("records")

    axes_data = {
        axe: df_q[df_q["axe"] == axe]["code"].tolist()
        for axe in df_q["axe"].unique()
    }

    # =========================
    # FIN QUESTIONNAIRE
    # =========================
    if st.session_state.q_index >= len(questions):
        finaliser_questionnaire(axes_data)
        return

    # =========================
    # QUESTION COURANTE
    # =========================
    q = questions[st.session_state.q_index]

    st.subheader(f"Axe : {q['axe']}")
    st.write(q["question"])

    valeur = st.select_slider(
        "Votre réponse",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: [
            "Pas du tout d’accord",
            "Pas d’accord",
            "Neutre",
            "D’accord",
            "Tout à fait d’accord"
        ][x - 1],
        key=f"q_{q['code']}"
    )

    st.session_state.responses[q["code"]] = valeur

    # =========================
    # PROGRESSION
    # =========================
    st.progress((st.session_state.q_index + 1) / len(questions))
    st.caption(f"Question {st.session_state.q_index + 1} / {len(questions)}")

    # =========================
    # NAVIGATION
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.q_index > 0:
            if st.button("⬅ Précédent"):
                st.session_state.q_index -= 1
                st.rerun()

    with col2:
        if st.button("Suivant ➡"):
            st.session_state.q_index += 1
            st.rerun()

# =========================
# FINALISATION & SAUVEGARDE
# =========================
def finaliser_questionnaire(axes_data):

    st.subheader("✅ Merci pour votre participation")

    r = st.session_state.responses

    # =========================
    # CALCUL DES SCORES
    # =========================
    scores_axes = {
        axe: round(sum(r[q] for q in qs) / len(qs), 2)
        for axe, qs in axes_data.items()
    }

    ici = round(sum(scores_axes.values()) / len(scores_axes) * 20, 1)

    st.metric("Indice de Culture d’Innovation (ICI)", f"{ici} / 100")

    # =========================
    # SAUVEGARDE
    # =========================
    df_out = pd.DataFrame([{
        "email": st.session_state.user["email"],
        "filiale": st.session_state.user["filiale"],
        **r,
        **scores_axes,
        "ici": ici,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    }])

    if os.path.exists(RESULTATS_FILE):
        df_out.to_csv(
            RESULTATS_FILE,
            mode="a",
            header=False,
            index=False,
            sep=";"
        )
    else:
        df_out.to_csv(
            RESULTATS_FILE,
            index=False,
            sep=";"
        )

    st.success("Vos réponses ont été enregistrées avec succès.")

    if st.button("🏁 Terminer"):
        # Nettoyage session questionnaire
        for key in ["q_index", "responses"]:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state.step = 0
        st.rerun()
