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
    # QUESTION COURANTE OU FIN
    # =========================
    if q_index < total_q:

        st.subheader(f"Question {q_index + 1} / {total_q}")
        st.write(QUESTIONS[q_index])

        answer = st.radio(
            "Votre réponse :",
            CHOICES,
            key=f"q_{q_index}"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("➡️ Question suivante", use_container_width=True):
            st.session_state.responses[q_index] = answer
            st.session_state.q_index += 1
            st.rerun()

    else:

        st.success("🎉 Merci pour votre participation !")
    
        st.markdown("""
        Votre contribution a bien été enregistrée.
    
        Elle sera analysée de manière **strictement anonyme** et **agrégée**
        avec l’ensemble des réponses collectées.
    
        Les résultats permettront d’identifier les leviers d’amélioration
        de la **culture d’innovation** au sein de l’organisation.
        """)
    
        st.markdown("<br>", unsafe_allow_html=True)
    
        if st.button("🏠 Retour à l’accueil", use_container_width=True):
            # Nettoyage session (optionnel)
            st.session_state.step = 0
            st.session_state.q_index = 0
            st.session_state.responses = {}
            st.rerun()

    # =========================
    # BARRE DE PROGRESSION (TOUJOURS EN BAS)
    # =========================
    st.markdown("<br><br>", unsafe_allow_html=True)

    progress = min(q_index / total_q, 1.0)
    st.progress(progress)

