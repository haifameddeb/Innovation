import streamlit as st

# Import des pages (Sprints séparés)
from APPacceuil import page_accueil
from APPquestionnaire import page_questionnaire

# =========================
# CONFIG GLOBALE
# =========================
st.set_page_config(
    page_title="InnoMeter",
    page_icon="🔵",
    layout="wide"
)

# =========================
# INITIALISATION SESSION
# =========================
# step :
# 0 = accueil / authentification
# 1 = questionnaire
# (les autres étapes viendront dans les prochains sprints)

if "step" not in st.session_state:
    st.session_state.step = 0

# =========================
# GARDE-FOUS DE SÉCURITÉ
# =========================

# 🔒 Interdire l’accès au questionnaire sans authentification
if st.session_state.step == 1 and "user" not in st.session_state:
    st.session_state.step = 0
    st.rerun()

# =========================
# ROUTEUR PRINCIPAL
# =========================

if st.session_state.step == 0:
    # Sprint 1 – Page d’accueil (FIGÉE)
    page_acceuil()

elif st.session_state.step == 1:
    # Sprint 2 – Questionnaire (FIGÉ)
    page_questionnaire()

else:
    # Sécurité : état inconnu → retour accueil
    st.session_state.step = 0
    st.rerun()







