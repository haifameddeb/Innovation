import streamlit as st
import pandas as pd
from datetime import date, datetime
import uuid
import os

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="InnoMeter – Administration",
    page_icon="🛠️",
    layout="centered"
)

CAMPAIGN_FILE = "campagnes.csv"

# =========================
# INIT FICHIER CAMPAGNES
# =========================
if not os.path.exists(CAMPAIGN_FILE):
    df_init = pd.DataFrame(
        columns=[
            "id_campagne",
            "nom",
            "description",
            "date_creation",
            "date_fin",
            "statut"
        ]
    )
    df_init.to_csv(CAMPAIGN_FILE, index=False)

def load_campagnes():
    return pd.read_csv(CAMPAIGN_FILE)

def save_campagnes(df):
    df.to_csv(CAMPAIGN_FILE, index=False)

# =========================
# HEADER
# =========================
st.title("🛠️ InnoMeter – Administration")
st.subheader("Gestion des campagnes de diagnostic")

email_admin = st.session_state.get("user", {}).get("email", "admin")
st.markdown(f"👋 **Bienvenue {email_admin}**")

st.divider()

# =========================
# LISTE DES CAMPAGNES
# =========================
st.markdown("## 📋 Campagnes")

df_campagnes = load_campagnes()

if df_campagnes.empty:
    st.info("Aucune campagne à afficher.")
else:
    st.dataframe(df_campagnes, use_container_width=True)

st.divider()

# =========================
# FORMULAIRE CREATION
# =========================
st.markdown("## ➕ Créer une nouvelle campagne")

with st.form("form_create_campaign", clear_on_submit=True):

    nom = st.text_input(
        "Nom de la campagne",
        placeholder="Ex: 2025/T1"
    )

    description = st.text_area(
        "Description",
        placeholder="Description de la campagne"
    )

    date_fin = st.date_input(
        "Date de fin de la campagne",
        min_value=date.today(),
        value=date.today()
    )

    submitted = st.form_submit_button("Créer la campagne")

# =========================
# TRAITEMENT SUBMIT
# =========================
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

    df_campagnes = load_campagnes()
    df_campagnes = pd.concat(
        [df_campagnes, pd.DataFrame([new_campaign])],
        ignore_index=True
    )

    save_campagnes(df_campagnes)

    st.success("✅ Campagne créée avec succès.")
    st.rerun()
