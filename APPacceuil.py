import streamlit as st
import pandas as pd
import os

# =========================
# CONFIG
# =========================
INVITES_FILE = "invites.csv"

st.set_page_config(
    page_title="InnoMeter – Accès",
    page_icon="🔵",
    layout="centered"
)

# =========================
# HEADER
# =========================
st.markdown("<br>", unsafe_allow_html=True)

st.title("🔵 InnoMeter")
st.subheader("Le baromètre de la culture d’innovation")

st.markdown("""
<p style="font-size:16px; color:#555;">
Comment respire notre culture d’innovation ?<br>
Participez au baromètre <b>InnoMeter</b> pour mesurer l’indice de culture
d’innovation (ICI) de notre organisation.
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# FORMULAIRE EMAIL ONLY
# =========================
email = st.text_input("📧 Adresse email professionnelle")

if st.button("🚀 Démarrer le diagnostic", use_container_width=True):

    # --- Vérification existence fichier
    if not os.path.exists(INVITES_FILE):
        st.error("❌ Le fichier des invités est introuvable.")
        st.stop()

    # --- Lecture du fichier invités
    try:
        df_inv = pd.read_csv(INVITES_FILE, sep=";")
    except Exception as e:
        st.error("❌ Impossible de lire le fichier des invités.")
        st.stop()

    # --- Nettoyage des colonnes
    df_inv.columns = (
        df_inv.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # --- Vérification structure minimale
    if "email" not in df_inv.columns:
        st.error(
            "❌ Le fichier des invités doit contenir une colonne nommée 'email'.\n\n"
            f"Colonnes détectées : {list(df_inv.columns)}"
        )
        st.stop()

    # --- Recherche utilisateur
    user = df_inv[df_inv["email"].str.lower() == email.strip().lower()]

    if user.empty:
        st.error("❌ Cette adresse email n’est pas référencée dans la liste des invités.")
    else:
        user = user.iloc[0]

        # =========================
        # INITIALISATION SESSION
        # =========================
        st.session_state.user = user
        st.session_state.q_index = 0
        st.session_state.responses = {}

        # =========================
        # REDIRECTION
        # =========================
        admin_flag = str(user.get("admin", "")).strip().lower()

        if admin_flag == "oui":
            st.session_state.step = 99   # dashboard admin (Sprint 3)
        else:
            st.session_state.step = 1    # questionnaire (Sprint 2)

        st.rerun()

# =========================
# CONFIANCE & CITATION
# =========================
st.markdown("""
<div style="text-align:center; margin-top:40px; font-style:italic; color:#666;">
    « On n’améliore durablement que ce que l’on prend le temps de mesurer. »
</div>

<div style="text-align:center; margin-top:10px; font-size:12px; color:#888;">
    🔒 Vos réponses sont anonymes et analysées uniquement de manière collective.
</div>
""", unsafe_allow_html=True)
