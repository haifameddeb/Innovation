import streamlit as st
import pandas as pd
import os

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
# CHARGEMENT DES QUESTIONS
# =========================
@st.cache_data
def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        raise FileNotFoundError("Fichier questions_ici.xlsx introuvable")

    df = pd.read_excel(QUESTIONS_FILE, sheet_name=SHEET_NAME)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    required_cols = {"question", "axe"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            "Le fichier questions_ici.xlsx doit contenir "
            "au minimum les colonnes : question, axe"
        )

    df = df.reset_index(drop=True)
    return df


# =========================
# PAGE QUESTIONNAIRE
# =========================
def page_questionnaire():

    # =========================
    # SÉCURITÉ
    # =========================
    if "user" not in st.session_state:
        st.session_state.step = 0
        st.rerun()

    # =========================
    # CHARGEMENT QUESTIONS
    # =========================
    try:
        df_questions = load_questions()
    except Exception as e:
        st.error(f"❌ {e}")
        return

    total_q = len(df_questions)

    # =========================
    # INIT SESSION
    # =========================
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0

    if "responses" not in st.session_state:
        st.session_state.responses = []

    q_index = st.session_state.q_index

    # =========================
    # HEADER
    # =========================
    st.title("🧠 Diagnostic InnoMeter")
    st.caption(f"👤 Participant : {st.session_state.user.get('email')}")
    st.markdown("---")

    # =========================
    # FIN QUESTIONNAIRE
    # =========================
    if q_index >= total_q:
        st.success("🎉 Merci pour votre participation !")

        st.markdown("""
        Votre contribution a bien été enregistrée.

        Elle sera analysée de manière **strictement anonyme** et **agrégée**
        avec l’ensemble des réponses collectées.

        Les résultats permettront d’identifier les leviers d’amélioration
        de la **culture d’innovation** au sein de l’organisation.
        """)

        if st.button("🏠 Retour à l’accueil", use_container_width=True):
            st.session_state.step = 0
            st.session_state.q_index = 0
            st.session_state.responses = []
            st.rerun()

        # Barre pleine en fin
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.progress(1.0)

        return

    # =========================
    # QUESTION COURANTE
    # =========================
    row = df_questions.iloc[q_index]
    question_text = row["question"]
    axe = row["axe"]

    st.subheader(f"Question {q_index + 1} / {total_q}")
    st.caption(f"🧭 Axe : {axe}")
    st.write(question_text)

    answer = st.radio(
        "Votre réponse :",
        CHOICES,
        key=f"q_{q_index}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("➡️ Question suivante", use_container_width=True):
        st.session_state.responses.append({
            "email": st.session_state.user.get("email"),
            "question": question_text,
            "axe": axe,
            "reponse": answer
        })

        st.session_state.q_index += 1
        st.rerun()

    # =========================
    # BARRE DE PROGRESSION (EN BAS)
    # =========================
    st.markdown("<br><br>", unsafe_allow_html=True)
    progress = min(q_index / total_q, 1.0)
    st.progress(progress)
