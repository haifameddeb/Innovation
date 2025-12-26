import streamlit as st
import pandas as pd
import os

INVITES_FILE = "invites.csv"

# =========================
# OUTILS
# =========================
def load_invites():
    try:
        df = pd.read_csv(INVITES_FILE, sep=None, engine="python")
    except Exception:
        return None

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )
    return df


def check_invitation(email):
    df_inv = load_invites()
    if df_inv is None or "email" not in df_inv.columns:
        return False

    return email.lower() in df_inv["email"].astype(str).str.lower().values


# =========================
# PAGE QUESTIONNAIRE
# =========================
def page_questionnaire():

    # 🔐 Sécurité : accès uniquement après accueil
    if "user" not in st.session_state:
        st.error("⛔ Accès non autorisé.")
        st.session_state.step = 0
        st.rerun()

    email_user = str(st.session_state.user.get("email", "")).strip().lower()

    # 🔎 Vérification invitation (robuste)
    if not check_invitation(email_user):
        st.error("❌ Vous n’êtes pas autorisé à répondre à ce questionnaire.")
        st.session_state.step = 0
        st.rerun()

    # =========================
    # UI QUESTIONNAIRE (TEST)
    # =========================
    st.title("🧠 Diagnostic InnoMeter")
    st.write(f"👤 Participant : **{email_user}**")

    st.markdown("---")

    st.subheader("Question 1")
    q1 = st.slider(
        "Dans mon organisation, les nouvelles idées sont encouragées.",
        1, 5, 3
    )

    if st.button("➡️ Question suivante"):
        st.success("✅ Questionnaire lancé avec succès !")
