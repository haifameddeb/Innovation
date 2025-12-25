import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv
import os
from datetime import datetime

# ============================
# CONFIGURATION
# ============================
INVITES_FILE = "invites.csv"
RESULTATS_FILE = "resultats_innovation.csv"
QUESTIONS_FILE = "questions.xlsx"

st.set_page_config(
    page_title="Indice de Culture de l’Innovation (ICI)",
    layout="centered"
)

# ============================
# SESSION STATE
# ============================
for k, v in {
    "step": 0,
    "current_q": 0,
    "responses": {},
    "invite": None,
}.items():
    st.session_state.setdefault(k, v)

# ============================
# CHARGEMENT QUESTIONS
# ============================
df_q = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
axes = df_q["axe"].unique().tolist()
questions_sequence = df_q.to_dict("records")

# ============================
# FONCTIONS
# ============================
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

# ============================
# STEP 0 – AUTHENTIFICATION
# ============================
if st.session_state.step == 0:
    st.title("🔐 Accès au diagnostic ICI")

    email = st.text_input("Email")
    code = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        invite = verifier_acces(email, code)
        if invite:
            st.session_state.invite = invite
            if invite["admin"] == "OUI":
                st.info("Accès administrateur")
                st.session_state.step = 99
            elif invite["statut"] == "OUI":
                st.warning("Vous avez déjà répondu.")
            else:
                st.session_state.step = 1
            st.rerun()
        else:
            st.error("Accès refusé")

# ============================
# STEP 1 – QUESTIONNAIRE
# ============================
elif st.session_state.step == 1:
    q = questions_sequence[st.session_state.current_q]
    st.subheader(q["axe"])
    st.write(q["question"])

    st.session_state.responses[q["code"]] = st.select_slider(
        "Votre réponse",
        [1,2,3,4,5],
        format_func=lambda x: ["Pas du tout d’accord","Pas d’accord","Neutre","D’accord","Tout à fait"][x-1]
    )

    progress = (st.session_state.current_q + 1) / len(questions_sequence)
    st.progress(progress)

    if st.button("Suivant"):
        if st.session_state.current_q < len(questions_sequence) - 1:
            st.session_state.current_q += 1
        else:
            st.session_state.step = 2
        st.rerun()

# ============================
# STEP 2 – RÉSULTATS UTILISATEUR
# ============================
elif st.session_state.step == 2:
    df_resp = pd.DataFrame.from_dict(st.session_state.responses, orient="index", columns=["score"])
    df_merge = df_q.merge(df_resp, left_on="code", right_index=True)

    scores_axes = df_merge.groupby("axe")["score"].mean()
    ici = scores_axes.mean() * 20

    marquer_repondu(st.session_state.invite["email"])

    archiver({
        "email": st.session_state.invite["email"],
        "filiale": st.session_state.invite["filiale"],
        **st.session_state.responses,
        **scores_axes.to_dict(),
        "ICI": round(ici, 2),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    st.success(f"Score ICI : {ici:.0f}/100")

    fig = go.Figure(go.Scatterpolar(
        r=list(scores_axes.values) + [scores_axes.values[0]],
        theta=list(scores_axes.index) + [scores_axes.index[0]],
        fill="toself"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,5])))
    st.plotly_chart(fig)

    if st.button("⬅️ Retour à l’accueil"):
        st.session_state.step = 0
        st.session_state.current_q = 0
        st.session_state.responses = {}
        st.rerun()

# ============================
# STEP 99 – DASHBOARD ADMIN
# ============================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Administrateur – ICI")

    df_inv = pd.read_csv(INVITES_FILE)

    if os.path.exists(RESULTATS_FILE) and os.path.getsize(RESULTATS_FILE) > 0:
        try:
            df_res = pd.read_csv(RESULTATS_FILE)
        except pd.errors.EmptyDataError:
            df_res = pd.DataFrame()
    else:
        df_res = pd.DataFrame()

    col1, col2, col3 = st.columns(3)
    col1.metric("Invités", len(df_inv))
    col2.metric("Réponses", len(df_inv[df_inv.statut=="OUI"]))
    col3.metric("Taux de participation",
        f"{round(len(df_inv[df_inv.statut=='OUI'])/len(df_inv)*100,1)} %")

    if not df_res.empty:
        st.subheader("📊 ICI moyen par filiale")
        fig = px.bar(df_res.groupby("filiale")["ICI"].mean().reset_index(),
                     x="filiale", y="ICI")
        st.plotly_chart(fig)

    st.subheader("📋 Suivi des invités")
    st.dataframe(df_inv, use_container_width=True)

    if st.button("⬅️ Déconnexion"):
        st.session_state.step = 0
        st.rerun()
