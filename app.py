import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ================== CONFIG PAGE ==================
st.set_page_config(
    page_title="Indice de Culture de l'Innovation (ICI)",
    layout="wide"
)

# ================== GOOGLE SHEETS ==================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open("ICI_Diagnostic")

ws_invites = sheet.worksheet("invites")
ws_reponses = sheet.worksheet("reponses")

def load_invites():
    return pd.DataFrame(ws_invites.get_all_records())

def save_invites(df):
    ws_invites.clear()
    ws_invites.update([df.columns.values.tolist()] + df.values.tolist())

def add_reponse(data):
    ws_reponses.append_row(list(data.values()))

# ================== QUESTIONS ==================
questions = {
    "Q1": "Si je tente une nouvelle approche et que ça ne marche pas, mon manager considère cela comme un apprentissage.",
    "Q2": "Dans mon équipe, on encourage les idées un peu 'folles' ou différentes.",
    "Q3": "Je me sens à l'aise pour exprimer une opinion contraire à celle de mes supérieurs.",
    "Q4": "Nous observons régulièrement ce que font nos concurrents ou d'autres secteurs.",
    "Q5": "Chaque collaborateur peut apporter une idée majeure au groupe.",
    "Q6": "On nous incite à sortir de notre bulle pour rencontrer d'autres départements.",
    "Q7": "Face à un problème, nous cherchons une solution plutôt qu'un coupable.",
    "Q8": "Nous savons changer nos habitudes rapidement si nécessaire.",
    "Q9": "‘On a toujours fait comme ça’ est rarement entendu ici.",
    "Q10": "Je sais vers qui me tourner pour tester une idée.",
    "Q11": "Les collègues partagent volontiers leurs informations.",
    "Q12": "La direction croit réellement en notre capacité à innover."
}

axes = {
    "Audace": ["Q1", "Q2", "Q3"],
    "Curiosité": ["Q4", "Q5", "Q6"],
    "Agilité": ["Q7", "Q8", "Q9"],
    "Énergie": ["Q10", "Q11", "Q12"]
}

LIKERT = {
    1: "1 - Pas du tout d'accord",
    2: "2 - Pas d'accord",
    3: "3 - Neutre",
    4: "4 - D'accord",
    5: "5 - Tout à fait d'accord"
}

# ================== AUTH ==================
st.title("🚀 Indice de Culture de l'Innovation (ICI)")

mode = st.sidebar.selectbox("Accès", ["Invité", "Admin"])

df_invites = load_invites()

# =
