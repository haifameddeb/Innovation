import streamlit as st
import pandas as pd
import os
from datetime import date

# =========================
# CONFIG
# =========================
CAMPAIGN_FILE = "campagnes.csv"

st.set_page_config(
    page_title="InnoMeter – Administration",
    page_icon="🛠️",
    layout="wide"
)

# =========================
# SESSION INIT (SAFE)
# =========================
if "admin_email" not in st.session_state:
    st.session_state.admin_email = "haifa.meddeb@rose-blanche.com"

if "camp_nom" not in st.session_state:
    st.session_state.camp_nom = ""

if "camp_desc" not in st.session_state:
    st.session_state.camp_desc = ""

if "camp_date_fin" not in st.session_state:
    st.session_state.camp_date_fin = date.today()

# =========================
# UTILS
# =========================
def load_campaigns():
    if not os.path.exists(CAMPAIGN_FILE):
        return pd.DataFrame(columns=[
            "nom", "description", "date_fin", "statut", "date_creation"
        ])
    return pd.read_csv(CAMPAIGN_FILE, sep=";", parse_dates=["date_fin", "date_creation"])


def save_campaign(df):
    df.to_csv(CAMPAIGN_FILE, sep=";", index=False)


def add_campaign(nom, desc, date_fin):
    df = load_campaigns()

    new_row = {
        "nom": nom,
        "description": desc,
        "date_fin": date_fin,
        "statut": "brouillon",
        "date_creation": date.today()
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_campaign(df)


def update_campaign_status(index, new_status):
    df = load_campaigns()
    df.loc[index, "statut"] = new_status
    save_campaign(df)


def delete_campaign(index):
    df = load_campaigns()
    df = df.drop(index)
    save_campaign(df)

# =========================
# HEADER
# =========================
st.title("🛠️ InnoMeter – Administration")
st.subheader("Gestion des campagnes de diagnostic")

st.markdown(f"👋 **Bienvenue {st.session_state.admin_email}**")
st.markdown("---")

# =========================
# LISTE DES CAMPAGNES
# =========================
st.markdown("### 📋 Campagnes")

df_camp = load_campaigns()

if df_camp.empty:
    st.info("Aucune campagne à afficher.")
else:
    for idx, row in df_camp.iterrows():
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

            col1.markdown(f"**{row['nom']}**")
            col1.markdown(row["description"])

            col2.markdown(f"📅 Fin : {row['date_fin'].date()}")
            col3.markdown(f"📌 Statut : **{row['statut']}**")

            # Actions
            with col4:
                if row["statut"] == "brouillon":
                    if st.button("🚀 Publier", key=f"pub_{idx}"):
                        update_campaign_status(idx, "publiée")
                        st.rerun()

                    if st.button("🗑️ Supprimer", key=f"del_{idx}"):
                        delete_campaign(idx)
                        st.rerun()

                elif row["statut"] == "publiée":
                    if st.button("📦 Archiver", key=f"arch_{idx}"):
                        update_campaign_status(idx, "archivée")
                        st.rerun()

# =========================
# CREATION CAMPAGNE
# =========================
st.markdown("---")
st.markdown("## ➕ Créer une nouvelle campagne")

with st.form("create_campaign"):
    camp_nom = st.text_input(
        "Nom de la campagne",
        key="camp_nom"
    )

    camp_desc = st.text_area(
        "Description",
        key="camp_desc"
    )

    camp_date_fin = st.date_input(
        "Date de fin de la campagne",
        min_value=date.today(),
        key="camp_date_fin"
    )

    submit = st.form_submit_button("Créer la campagne")

# =========================
# TRAITEMENT FORMULAIRE
# =========================
if submit:
    if not camp_nom.strip():
        st.error("❌ Le nom de la campagne est obligatoire.")
    else:
        add_campaign(
            nom=camp_nom.strip(),
            desc=camp_desc.strip(),
            date_fin=camp_date_fin
        )

        st.success("✅ Campagne créée avec succès")

        # Reset propre
        st.session_state.camp_nom = ""
        st.session_state.camp_desc = ""
        st.session_state.camp_date_fin = date.today()

        st.rerun()
