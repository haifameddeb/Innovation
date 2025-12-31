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

# Init champs formulaire
for key in ["camp_nom", "camp_desc", "camp_date_fin"]:
    if key not in st.session_state:
        st.session_state[key] = ""

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

        df_inv = load_invites()

        if not is_admin(email, df_inv):
            st.error("❌ Accès refusé.")
            st.stop()

        st.session_state.admin_authenticated = True
        st.session_state.admin_email = email
        st.rerun()

    st.stop()

# =========================
# DASHBOARD CAMPAGNES
# =========================
df_campagnes = load_campagnes()

st.success(f"👋 Bienvenue {st.session_state.admin_email}")
st.divider()

# Filtres
show_archived = st.checkbox("Afficher les campagnes archivées", value=False)

if not show_archived:
    df_view = df_campagnes[df_campagnes["statut"] != "Archivée"]
else:
    df_view = df_campagnes

# =========================
# LISTE CAMPAGNES
# =========================
st.subheader("📋 Campagnes")

if df_view.empty:
    st.info("Aucune campagne à afficher.")
else:
    for _, row in df_view.sort_values("date_creation", ascending=False).iterrows():

        with st.expander(f"📌 {row['nom']} — {row['statut']}"):

            st.write(row["description"])
            st.caption(f"Créée le {row['date_creation']} | Fin : {row['date_fin']}")

            col1, col2 = st.columns(2)

            # 🗑️ SUPPRESSION (Brouillon uniquement)
            if row["statut"] == "Brouillon":
                with col1:
                    if st.button("🗑️ Supprimer", key=f"del_{row['id_campagne']}"):
                        df_campagnes = df_campagnes[
                            df_campagnes["id_campagne"] != row["id_campagne"]
                        ]
                        save_campagnes(df_campagnes)
                        st.rerun()

            # 📦 ARCHIVAGE
            if row["statut"] != "Archivée":
                with col2:
                    if st.button("📦 Archiver", key=f"arch_{row['id_campagne']}"):
                        df_campagnes.loc[
                            df_campagnes["id_campagne"] == row["id_campagne"],
                            "statut"
                        ] = "Archivée"
                        save_campagnes(df_campagnes)
                        st.rerun()

st.divider()

# =========================
# CREATION CAMPAGNE
# =========================
st.subheader("➕ Créer une nouvelle campagne")

with st.form("create_campaign_form"):

    nom = st.text_input("Nom de la campagne", key="camp_nom")
    description = st.text_area("Description", key="camp_desc")
    date_fin = st.date_input(
        "Date de fin de la campagne",
        min_value=date.today(),
        key="camp_date_fin"
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

        # 🧹 Reset formulaire
        st.session_state.camp_nom = ""
        st.session_state.camp_desc = ""
        st.session_state.camp_date_fin = date.today()

        st.success("✅ Campagne créée.")
        st.rerun()
