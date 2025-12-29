import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import uuid

# =========================
# CONFIG
# =========================
INVITES_FILE = "invites.csv"
DATA_DIR = "data"
CAMPAGNES_FILE = os.path.join(DATA_DIR, "campagnes.csv")

st.set_page_config(
    page_title="InnoMeter – Administration",
    page_icon="🛠️",
    layout="wide"
)

# =========================
# UTILS
# =========================
def ensure_data_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(CAMPAGNES_FILE):
        df = pd.DataFrame(columns=[
            "id_campagne",
            "nom",
            "description",
            "date_creation",
            "date_fin",
            "statut"
        ])
        df.to_csv(CAMPAGNES_FILE, index=False)


def load_invites():
    if not os.path.exists(INVITES_FILE):
        st.error("❌ Fichier invites.csv introuvable.")
        st.stop()

    df = pd.read_csv(INVITES_FILE, sep=None, engine="python")
    df.columns = df.columns.str.strip().str.lower()
    return df


def is_admin(email, df_inv):
    user = df_inv[df_inv["email"].str.lower() == email.lower()]
    if user.empty:
        return False
    return str(user.iloc[0].get("admin", "")).strip().lower() == "oui"


def load_campagnes():
    return pd.read_csv(CAMPAGNES_FILE)


def save_campagnes(df):
    df.to_csv(CAMPAGNES_FILE, index=False)


# =========================
# INIT
# =========================
ensure_data_files()

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# =========================
# HEADER
# =========================
st.title("🛠️ InnoMeter – Administration")
st.caption("Gestion des campagnes de diagnostic")
st.divider()

# =========================
# AUTH ADMIN
# =========================
if not st.session_state.admin_authenticated:

    st.subheader("🔐 Connexion administrateur")
    email = st.text_input("📧 Adresse email administrateur")

    if st.button("Se connecter", use_container_width=True):

        if not email or not email.strip():
            st.error("❌ Veuillez saisir une adresse email.")
            st.stop()

        df_inv = load_invites()

        if not is_admin(email, df_inv):
            st.error("❌ Accès refusé. Vous n’êtes pas administrateur.")
            st.stop()

        st.session_state.admin_authenticated = True
        st.session_state.admin_email = email
        st.success("✅ Authentification réussie")
        st.rerun()

    st.stop()

# =========================
# DASHBOARD CAMPAGNES
# =========================
st.success(f"👋 Bienvenue {st.session_state.admin_email}")
st.divider()

df_campagnes = load_campagnes()

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 Campagnes existantes")

    if df_campagnes.empty:
        st.info("Aucune campagne créée pour le moment.")
    else:
        st.dataframe(
            df_campagnes.sort_values("date_creation", ascending=False),
            use_container_width=True,
            hide_index=True
        )

with col2:
    st.subheader("📊 Indicateurs")
    st.metric("Nombre de campagnes", len(df_campagnes))
    st.metric(
        "Campagnes en cours",
        len(df_campagnes[df_campagnes["statut"] == "En cours"])
    )

st.divider()

# =========================
# CREATION CAMPAGNE
# =========================
st.subheader("➕ Créer une nouvelle campagne")

with st.form("create_campaign_form"):
    nom = st.text_input("Nom de la campagne")
    description = st.text_area("Description")
    date_fin = st.date_input(
        "Date de fin de la campagne",
        min_value=date.today()
    )

    submitted = st.form_submit_button("Créer la campagne")

    if submitted:
        if not nom.strip():
            st.error("❌ Le nom de la campagne est obligatoire.")
            st.stop()

        new_campaign = {
            "id_campagne": str(uuid.uuid4())[:8],
            "nom": nom.strip(),
            "description": description.strip(),
            "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "date_fin": date_fin.strftime("%Y-%m-%d"),
            "statut": "Brouillon"
        }

        df_campagnes = pd.concat(
            [df_campagnes, pd.DataFrame([new_campaign])],
            ignore_index=True
        )

        save_campagnes(df_campagnes)

        st.success("✅ Campagne créée avec succès.")
        st.rerun()
