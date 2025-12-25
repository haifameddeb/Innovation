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

# ==================================================
# SESSION STATE
# ==================================================
if "step" not in st.session_state:
    st.session_state.step = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}

# ==================================================
# QUESTIONNAIRE STRUCTURE
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
# FONCTIONS DATA
# ==================================================
def verifier_acces(email, code):
    with open("invites.csv", encoding="utf-8") as f:
        for p in csv.DictReader(f):
            if p["email"].lower() == email.lower() and p["code"] == code:
                if p.get("admin", "NON") == "OUI":
                    return "ADMIN", p
                return ("DEJA", p) if p["statut"] == "OUI" else ("OK", p)
    return "REFUSE", None


def marquer_repondu(email):
    rows = []
    with open("invites.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        if r["email"].lower() == email.lower():
            r["statut"] = "OUI"
            r["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    with open("invites.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def archiver(data):
    file = "resultats_innovation.csv"
    df = pd.DataFrame([data])
    if not os.path.exists(file):
        df.to_csv(file, index=False)
    else:
        df.to_csv(file, mode="a", header=False, index=False)

# ==================================================
# STEP 0 – LOGIN
# ==================================================
if st.session_state.step == 0:
    st.title("🔐 Accès au diagnostic ICI")

    email = st.text_input("Adresse email")
    code = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        statut, personne = verifier_acces(email, code)

        if statut == "ADMIN":
            st.info("🛡️ Accès administrateur détecté")
            st.session_state.invite = personne
            st.session_state.step = 99
            st.rerun()

        elif statut == "OK":
            st.session_state.invite = personne
            st.session_state.step = 1
            st.rerun()

        elif statut == "DEJA":
            st.warning("Vous avez déjà répondu au questionnaire.")
        else:
            st.error("Identifiants incorrects.")

# ==================================================
# STEP 1 – QUESTIONS (UX AMÉLIORÉE)
# ==================================================
elif st.session_state.step == 1:
    axe, q = questions_sequence[st.session_state.current_q]
    q_index = axes_data[axe].index(q) + 1

    st.subheader(f"📌 Axe : {axe}")
    st.caption(f"Question {q_index} / 3")

    st.write(questions_text[q])

    st.session_state.responses[q] = st.select_slider(
        "Votre réponse",
        [1, 2, 3, 4, 5],
        format_func=lambda x: [
            "Pas du tout d’accord",
            "Pas d’accord",
            "Neutre",
            "D’accord",
            "Tout à fait"
        ][x - 1],
        key=q
    )

    st.progress((st.session_state.current_q + 1) / len(questions_sequence))

    if st.button("Suivant ➡️"):
        if st.session_state.current_q < len(questions_sequence) - 1:
            st.session_state.current_q += 1
        else:
            st.session_state.step = 2
        st.rerun()

# ==================================================
# STEP 2 – RÉSULTATS INDIVIDUELS
# ==================================================
elif st.session_state.step == 2:
    r = st.session_state.responses
    scores = {axe: sum(r[q] for q in qs) / 3 for axe, qs in axes_data.items()}
    ici = sum(scores.values()) / 4 * 20

    marquer_repondu(st.session_state.invite["email"])
    archiver({
        "email": st.session_state.invite["email"],
        **r,
        **scores,
        "ICI": round(ici, 2),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    st.success(f"Score ICI : {ici:.0f}/100")

    # Radar individuel
    fig = go.Figure(go.Scatterpolar(
        r=list(scores.values()) + [list(scores.values())[0]],
        theta=list(scores.keys()) + [list(scores.keys())[0]],
        fill="toself"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5])))
    st.plotly_chart(fig)

# ==================================================
# STEP 99 – DASHBOARD ADMIN AVANCÉ
# ==================================================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Administrateur – ICI")

    df = pd.read_csv("resultats_innovation.csv")

    # Moyennes par axe
    moyennes = df[list(axes_data.keys())].mean().reset_index()
    moyennes.columns = ["Axe", "Score"]

    st.subheader("📊 Moyenne par axe")
    st.plotly_chart(
        px.bar(moyennes, x="Axe", y="Score", range_y=[1, 5]),
        use_container_width=True
    )

    st.subheader("🧭 Radar moyen global")
    fig = go.Figure(go.Scatterpolar(
        r=moyennes["Score"].tolist() + [moyennes["Score"].tolist()[0]],
        theta=moyennes["Axe"].tolist() + [moyennes["Axe"].tolist()[0]],
        fill="toself"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5])))
    st.plotly_chart(fig)

    st.download_button(
        "⬇️ Export résultats (Excel)",
        df.to_csv(index=False),
        "resultats_ici.csv"
    )

    if st.button("⬅️ Déconnexion"):
        st.session_state.step = 0
        st.session_state.current_q = 0
        st.session_state.responses = {}
        st.rerun()
