import streamlit as st

# =========================
# IMPORT DES PAGES
# (noms EXACTS des fichiers)
# =========================
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
if "step" not in st.session_state:
    st.session_state.step = 0

# =========================
# GARDE-FOU SÉCURITÉ
# =========================
# Empêche l’accès au questionnaire sans authentification
if st.session_state.step == 1 and "user" not in st.session_state:
    st.session_state.step = 0
    st.rerun()

# =========================
# ROUTEUR PRINCIPAL
# =========================
if st.session_state.step == 0:
    page_accueil()

elif st.session_state.step == 1:
    page_questionnaire()

else:
    # état inconnu → retour accueil
    st.session_state.step = 0
    st.rerun()
