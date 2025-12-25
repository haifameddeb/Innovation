import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv
import os
from datetime import datetime

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(
    page_title="Indice de Culture de l'Innovation (ICI)",
    layout="centered"
)

INVITES_FILE = "invites.csv"
RESULTATS_FILE = "resultats_innovation.csv"

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
# QUESTIONNAIRE
# ==================================================
axes_data = {
    "Audace": ["Q1", "Q2", "Q3"],
    "Curiosité": ["Q4", "Q5", "Q6"],
    "Agilité": ["Q7", "Q8", "Q9"],
    "Énergie": ["Q10", "Q11", "Q12"]
}

questions_text = {
    "Q1": "Si je tente une nouvelle approche et que ça ne marche pas, mon manager considère cela comme un apprentissage.",
    "Q2": "Dans mon équipe, on encourage les idées originales.",
    "Q3": "Je me sens à l’aise pour exprimer une opinion différente.",
    "Q4": "Nous observons régulièrement ce que font nos concurrents.",
    "Q5": "Chaque collaborateur peut apporter une idée majeure.",
    "Q6": "Les échanges inter-départements sont encouragés.",
    "Q7": "On cherche une solution plutôt qu’un coupable.",
    "Q8": "Nous changeons rapidement nos habitudes si nécessaire.",
    "Q9": "« On a toujours fait comme ça » est rare ici.",
    "Q10": "Je sais vers qui me tourner pour tester une idée.",
    "Q11": "Les informations sont partagées librement.",
    "Q12": "La direction croit en notre capacité à innover."
}

questions_sequence = [(axe, q) for axe in axes_data for q in axes_data[axe]]

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
                st.info("🛠 Accès administrateur détecté")
                st.session_state.step = 99
            else:
                st.session_state.step = 10
            st.rerun()
        else:
            st.error("Accès refusé")

# ==================================================
# STEP 10 – PAGE DE LANCEMENT
# ==================================================
elif st.session_state.step == 10:
    st.markdown("## 🚀 Comment respire notre culture ?")
    st.markdown(
        "Participez au baromètre anonyme pour mesurer "
        "l’indice de culture de l’innovation (ICI)."
    )

    if st.button("▶️ Démarrer le test"):
        st.session_state.step = 1
        st.rerun()

    if st.button("⬅️ Retour à l’authentification"):
        st.session_state.clear()
        st.session_state.step = 0
        st.rerun()

# ==================================================
# STEP 1 – QUESTIONS
# ==================================================
elif st.session_state.step == 1:
    axe, q = questions_sequence[st.session_state.current_q]

    st.subheader(f"🧩 Axe : {axe}")
    st.write(questions_text[q])

    st.session_state.responses[q] = st.select_slider(
        "Votre réponse",
        [1,2,3,4,5],
        format_func=lambda x: ["Pas du tout d’accord","Pas d’accord","Neutre","D’accord","Tout à fait"][x-1],
        key=q
    )

    st.progress((st.session_state.current_q + 1) / len(questions_sequence))

    if st.button("Suivant"):
        if st.session_state.current_q < len(questions_sequence) - 1:
            st.session_state.current_q += 1
        else:
            st.session_state.step = 2
        st.rerun()

# ==================================================
# STEP 2 – RÉSULTATS (NON ADMIN)
# ==================================================
elif st.session_state.step == 2:
    st.markdown("## 🎉 Vos résultats ICI")

    r = st.session_state.responses
    scores = {axe: sum(r[q] for q in qs)/3 for axe, qs in axes_data.items()}
    ici = sum(scores.values()) / 4 * 20

    marquer_repondu(st.session_state.invite["email"])
    archiver({
        "email": st.session_state.invite["email"],
        **r,
        **scores,
        "ICI": round(ici,2),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    st.success(f"🌱 Indice ICI : **{ici:.0f}/100**")

    # Radar
    fig_radar = go.Figure(go.Scatterpolar(
        r=list(scores.values()) + [list(scores.values())[0]],
        theta=list(scores.keys()) + [list(scores.keys())[0]],
        fill='toself'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(range=[0,5])),
        showlegend=False
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Histogramme
    df_axes = pd.DataFrame({
        "Axe": list(scores.keys()),
        "Score": list(scores.values())
    })
    fig_bar = px.bar(df_axes, x="Axe", y="Score", range_y=[0,5])
    st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("⬅️ Retour à l’authentification"):
        st.session_state.clear()
        st.session_state.step = 0
        st.rerun()

# ==================================================
# STEP 99 – DASHBOARD ADMIN
# ==================================================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Administrateur – ICI")

    df_inv = pd.read_csv(INVITES_FILE)
    df_res = pd.read_csv(RESULTATS_FILE) if os.path.exists(RESULTATS_FILE) else pd.DataFrame()

    col1,col2,col3 = st.columns(3)
    col1.metric("Invités", len(df_inv))
    col2.metric("Réponses", len(df_inv[df_inv.statut=="OUI"]))
    col3.metric("Taux", f"{round(len(df_inv[df_inv.statut=='OUI'])/len(df_inv)*100,1)} %")

    st.subheader("📋 Suivi des invités")
    st.dataframe(df_inv, use_container_width=True)

    if not df_res.empty:
        st.subheader("📈 Résultats")
        st.dataframe(df_res, use_container_width=True)

    if st.button("⬅️ Déconnexion"):
        st.session_state.clear()
        st.session_state.step = 0
        st.rerun()
