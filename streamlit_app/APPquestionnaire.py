import streamlit as st
import pandas as pd
import os

from ICI_calcul import calcul_ici
from ICI_affichage import afficher_resultats

# =========================
# CONFIG
# =========================
QUESTIONS_FILE = "questions_ici.xlsx"
SHEET_NAME = "questions"

CHOICES = [
    "Pas du tout d’accord",
    "Plutôt pas d’accord",
    "Neutre",
    "Plutôt d’accord",
    "Tout à fait d’accord"
]

# =========================
# CHARGEMENT QUESTIONS
# =========================
@st.cache_data
def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        raise FileNotFoundError("❌ Fichier questions_ici.xlsx introuvable")

    df = pd.read_excel(QUESTIONS_FILE, sheet_name=SHEET_NAME)
    df.columns = df.columns.astype(str).str.strip().str.lower()

    if not {"question", "axe"}.issubset(df.columns):
        raise ValueError(
            "Le fichier questions_ici.xlsx doit contenir "
            "au minimum les colonnes : question, axe"
        )

    return df.reset_index(drop=True)


# =========================
# PAGE QUESTIONNAIRE
# =========================
def page_questionnaire():

    # =========================
    # SÉCURITÉ SESSION
    # =========================
    if "user" not in st.session_state:
        st.session_state.step = 0
        st.rerun()

    # =========================
    # CHARGEMENT QUESTIONS
    # =========================
    try:
        df_q = load_questions()
    except Exception as e:
        st.error(str(e))
        return

    total_q = len(df_q)

    # =========================
    # INITIALISATION SESSION (SPRINT 2)
    # =========================
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0

    if "responses" not in st.session_state or not isinstance(st.session_state.responses, list):
        st.session_state.responses = []

    q_index = st.session_state.q_index

    # =========================
    # HEADER (SPRINT 2)
    # =========================
    st.title("🧠 Diagnostic InnoMeter")
    st.caption(f"👤 Participant : {st.session_state.user.get('email')}")
    st.markdown("---")

    # =========================
    # FIN QUESTIONNAIRE → AFFICHAGE RÉSULTAT
    # =========================
    if q_index >= total_q:

        resultats = calcul_ici(st.session_state.responses)
        afficher_resultats(resultats)

        st.markdown("""
        ---
        🔒 Vos réponses sont traitées de manière strictement anonyme.
        """)

        st.progress(1.0)

        if st.button("🏠 Retour à l’accueil", use_container_width=True):
            st.session_state.step = 0
            st.session_state.q_index = 0
            st.session_state.responses = []
            st.rerun()

        return

    # =========================
    # QUESTION COURANTE (SPRINT 2)
    # =========================
    row = df_q.iloc[q_index]

    st.subheader(f"Question {q_index + 1} / {total_q}")
    st.caption(f"🧭 Axe : {row['axe']}")
    st.write(row["question"])

    answer = st.radio(
        "Votre réponse :",
        CHOICES,
        key=f"q_{q_index}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # QUESTION SUIVANTE (SPRINT 2)
    # =========================
    if st.button("➡️ Question suivante", use_container_width=True):

        # Sécurité absolue (Streamlit rerun)
        if "responses" not in st.session_state or not isinstance(st.session_state.responses, list):
            st.session_state.responses = []

        st.session_state.responses.append({
            "email": st.session_state.user.get("email"),
            "question": row["question"],
            "axe": row["axe"],
            "reponse": answer
        })

        st.session_state.q_index += 1
        st.rerun()

    # =========================
    # BARRE DE PROGRESSION (SPRINT 2)
    # =========================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.progress((q_index + 1) / total_q)
