import streamlit as st

# =========================
# QUESTIONS (SPRINT 2)
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

    # =========================
    # SÉCURITÉ
    # =========================
    if "user" not in st.session_state:
        st.session_state.step = 0
        st.rerun()

    # =========================
    # INITIALISATION SESSION
    # =========================
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

    st.markdown("---")

    # =========================
    # FIN DU QUESTIONNAIRE
    # =========================
    if q_index >= total_q:
        st.success("🎉 Merci pour votre participation !")
        st.write(
            "Vos réponses ont bien été enregistrées. "
            "Elles seront analysées de manière strictement anonyme."
        )

        # DEBUG (à retirer plus tard)
        st.write("🗂️ Réponses collectées :", st.session_state.responses)

        return

    # =========================
    # QUESTION COURANTE
    # =========================
    st.subheader(f"Question {q_index + 1} / {total_q}")
    st.write(QUESTIONS[q_index])

    answer = st.radio(
        "Votre réponse :",
        CHOICES,
        key=f"q_{q_index}"
    )

    # =========================
    # NAVIGATION
    # =========================
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("➡️ Question suivante", use_container_width=True):
        # Sauvegarde réponse
        st.session_state.responses[q_index] = answer

        # Question suivante
        st.session_state.q_index += 1
        st.rerun()

    # =========================
    # BARRE DE PROGRESSION (EN BAS)
    # =========================
    st.markdown("<br><br>", unsafe_allow_html=True)

    progress = min(q_index / total_q, 1.0)
    st.progress(progress)
