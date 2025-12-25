import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv
import os
from datetime import datetime

# ==================================================
# CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Indice de Culture de l'Innovation (ICI)",
    layout="centered"
)

INVITES_FILE = "invites.csv"
RESULTATS_FILE = "resultats_innovation.csv"
QUESTIONS_FILE = "questions_ici.xlsx"

# ==================================================
# CHARGEMENT DES QUESTIONS & INTERPRÉTATION
# ==================================================
df_questions = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
df_interp = pd.read_excel(QUESTIONS_FILE, sheet_name="interpretation")

axes_data = {
    axe: df_questions[df_questions["axe"] == axe]["id"].tolist()
    for axe in df_questions["axe"].unique()
}

questions_sequence = [
    (row["axe"], row["id"], row["question"])
    for _, row in df_questions.iterrows()
]

# ==================================================
# SESSION STATE
# ==================================================
if "step" not in st.session_state:
    st.session_state.step = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "invite" not in st.session_state:
    st.session_state.invite = None

# ==================================================
# FONCTIONS
# ==================================================
def verifier_acces(email, code):
    with open(INVITES_FILE, encoding="utf-8") as f:
        for p in csv.DictReader(f):
            if p["email"].lower() == email.lower() and p["code"] == code:
                return p
    return None

def marquer_repondu(email):
    rows = []
    with open(INVITES_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        if r["email"].lower() == email.lower():
            r["statut"] = "OUI"
            r["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    with open(INVITES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def archiver(data):
    df = pd.DataFrame([data])
    if not os.path.exists(RESULTATS_FILE):
        df.to_csv(RESULTATS_FILE, index=False)
    else:
        df.to_csv(RESULTATS_FILE, mode="a", header=False, index=False)

def determiner_maturite(score):
    ligne = df_interp[(df_interp["min"] <= score) & (score <= df_interp["max"])]
    if not ligne.empty:
        return ligne.iloc[0]["niveau"], ligne.iloc[0]["message"]
    return "Inconnu", ""

# ==================================================
# STEP 0 – AUTHENTIFICATION
# ==================================================
if st.session_state.step == 0:
    st.title("🔐 Accès au diagnostic ICI")

    email = st.text_input("Email")
    code = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        personne = verifier_acces(email, code)
        if personne:
            st.session_state.invite = personne
            if personne["admin"] == "OUI":
                st.session_state.step = 99
            else:
                st.session_state.step = 1
            st.rerun()
        else:
            st.error("Accès refusé")

# ==================================================
# STEP 1 – QUESTIONNAIRE
# ==================================================
elif st.session_state.step == 1:
    axe, qid, qtext = questions_sequence[st.session_state.current_q]

    st.subheader(f"Axe : {axe}")
    st.write(qtext)

    st.session_state.responses[qid] = st.select_slider(
        "Votre réponse",
        [1,2,3,4,5],
        format_func=lambda x: [
            "Pas du tout d’accord",
            "Pas d’accord",
            "Neutre",
            "D’accord",
            "Tout à fait d’accord"
        ][x-1]
    )

    st.progress((st.session_state.current_q+1)/len(questions_sequence))

    if st.button("Suivant"):
        if st.session_state.current_q < len(questions_sequence)-1:
            st.session_state.current_q += 1
        else:
            st.session_state.step = 2
        st.rerun()

# ==================================================
# STEP 2 – RÉSULTATS INDIVIDUELS
# ==================================================
elif st.session_state.step == 2:
    r = st.session_state.responses

    scores = {
        axe: sum(r[q] for q in qs) / len(qs)
        for axe, qs in axes_data.items()
    }

    ici = sum(scores.values()) / len(scores) * 20

    marquer_repondu(st.session_state.invite["email"])
    archiver({
        "email": st.session_state.invite["email"],
        "filiale": st.session_state.invite["filiale"],
        **scores,
        "ICI": round(ici,2),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    niveau, message = determiner_maturite(ici)

    st.success(f"Score ICI : {ici:.0f}/100")
    st.info(f"{niveau} — {message}")

    # Radar
    fig = go.Figure(go.Scatterpolar(
        r=list(scores.values()) + [list(scores.values())[0]],
        theta=list(scores.keys()) + [list(scores.keys())[0]],
        fill="toself"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,5])))
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Retour à l’authentification"):
        st.session_state.clear()
        st.session_state.step = 0
        st.rerun()

# ==================================================
# STEP 99 – DASHBOARD ADMIN (PAR FILIALE)
# ==================================================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Administrateur – ICI")

    df_inv = pd.read_csv(INVITES_FILE)
    df_res = pd.read_csv(RESULTATS_FILE)

    df_full = df_res.merge(
        df_inv[["email", "filiale"]],
        on="email",
        how="left"
    )

    st.subheader("📌 KPI globaux par filiale")

    kpi = (
        df_full
        .groupby("filiale")["ICI"]
        .agg(["mean","min","max","std","count"])
        .reset_index()
    )

    kpi.columns = [
        "Filiale","ICI moyen","ICI min","ICI max","Dispersion","Réponses"
    ]

    kpi["Niveau de maturité"] = kpi["ICI moyen"].apply(
        lambda x: determiner_maturite(x)[0]
    )

    st.dataframe(kpi, use_container_width=True)

    fig = px.bar(
        kpi,
        x="Filiale",
        y="ICI moyen",
        color="Niveau de maturité",
        range_y=[0,100],
        text="ICI moyen"
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Déconnexion"):
        st.session_state.clear()
        st.session_state.step = 0
        st.rerun()
