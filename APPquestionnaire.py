import streamlit as st

# =========================
# QUESTIONS (TEMPORAIRE)
# =========================
QUESTIONS = [
    "Dans mon organisation, les nouvelles idées sont encouragées.",
    "Les échecs sont perçus comme des opportunités d’apprentissage.",
    "Les collaborateurs disposent du temps nécessaire pour innover.",
    "Les outils technologiques soutiennent l’innovation.",
    "La direction soutient activement les initiatives innovantes."
]

CHOICES = [
    "Pas du tout d’accord",
    "Plutôt pas d’accord",
    "Neutre",
    "Plutôt d’accord",
    "Tout à fait d’accord"
]

# =========================
# PAGE QUESTIONNAIRE
# =========================
def page_questionnaire():

    # 🔐 Sécurité minimale
    if "user" not in st.session_state:
        st.session_state.step = 0
        st.rerun()

    # Initialisation
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    q_index = st.session_state.q_index
    total_q = len(QUESTIONS)

    # =========================
    # HEADER
    # =========================
    st.title("🧠 Diagnostic InnoMeter")
    st.caption(f"👤 Participant : {st.session_state.user.get('email')}")

    st.progress((q_index + 1) / total_q)

    st.markdown("---")

    # =========================
    # FIN DU QUESTIONNAIRE
    # =========================
    if q_index >= total_q:
        st.success("🎉 Merci pour votre participation !")
        st.write("Vos réponses ont bien été enregistrées.")
        st.write(st.session_state.responses)
        return

    # =========================
    # QUESTION COURANTE
    # =========================
    st.subheader(f"Question {q_index + 1}")
    st.write(QUESTIONS[q_index])

    answer = st.radio(
        "Votre réponse :",
        CHOICES,
        key=f"q_{q_index}"
    )

    # =========================
    # NAVIGATION
    # =========================
    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("➡️ Question suivante"):
            # Sauvegarde réponse
            st.session_state.responses[q_index] = answer

            # Passage à la question suivante
            st.session_state.q_index += 1
            st.rerun()
