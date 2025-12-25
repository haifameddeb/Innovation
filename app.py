import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import csv
import os
from datetime import datetime

# ==================================================
# CONFIGURATION PAGE
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
# DONNÉES QUESTIONNAIRE
# ==================================================
axes_data = {
    "Le Droit à l'Audace": ["Q1", "Q2", "Q3"],
    "La Curiosité au Quotidien": ["Q4", "Q5", "Q6"],
    "L'Agilité Mentale": ["Q7", "Q8", "Q9"],
    "L'Énergie Collective": ["Q10", "Q11", "Q12"]
}

questions_text = {
    "Q1": "Si je tente une nouvelle approche et que ça ne marche pas, mon manager considère cela comme un apprentissage plutôt que comme une faute.",
    "Q2": "Dans mon équipe, on encourage les idées un peu « folles » ou différentes.",
    "Q3": "Je me sens à l'aise pour exprimer une opinion contraire à celle de mes supérieurs.",
    "Q4": "Nous prenons régulièrement le temps d'observer ce que font nos concurrents ou d'autres secteurs.",
    "Q5": "Je crois que chaque collaborateur, quel que soit son poste, peut apporter une idée majeure au groupe.",
    "Q6": "On nous incite à sortir de notre « bulle » pour rencontrer des collègues d'autres départements.",
    "Q7": "Quand un problème survient, nous cherchons d'abord une solution plutôt qu'un coupable.",
    "Q8": "Nous sommes capables de changer nos habitudes rapidement si une meilleure façon de faire est proposée.",
    "Q9": "Ici, « on a toujours fait comme ça » est une phrase que l'on entend rarement.",
    "Q10": "Si j'ai une idée, je sais vers qui me tourner pour m'aider à la tester.",
    "Q11": "Mes collègues partagent volontiers leurs informations et leurs découvertes.",
    "Q12": "Je sens que la direction croit vraiment en notre capacité à inventer le futur du groupe."
}

questions_sequence = [(axe, q) for axe in axes_data for q in axes_data[axe]]
TOTAL_QUESTIONS = len(questions_sequence)

# ==================================================
# FONCTIONS MÉTIER
# ==================================================
def verifier_acces(email, code):
    with open("invites.csv", newline="", encoding="utf-8") as f:
        invites = list(csv.DictReader(f))

    for p in invites:
        if p["email"].lower() == email.lower() and p["code"] == code:
            if p["statut"] == "OUI":
                return "DEJA_REPONDU", p
            return "OK", p
    return "REFUSE", None


def marquer_comme_repondu(email):
    rows = []
    with open("invites.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["email"].lower() == email.lower():
                row["statut"] = "OUI"
                row["date_reponse"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            rows.append(row)

    with open("invites.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def interpreter_score_ici(score):
    if score < 50:
        return "🟥 Culture Silotée / Prudente", (
            "L’innovation est freinée par la peur du risque et un fonctionnement en silos."
        )
    elif score < 75:
        return "🟧 Culture En Éveil", (
            "Les bases de l’innovation existent, mais des blocages persistent."
        )
    return "🟩 Culture Innovante", (
        "L’innovation est ancrée dans les réflexes collectifs."
    )


def analyse_par_axe(score):
    if score < 3:
        return "🔴 Axe fragile – prioritaire"
    elif score < 4:
        return "🟠 Axe à renforcer"
    return "🟢 Axe solide"


def archiver_reponse(data):
    filename = "resultats_innovation.csv"
    df = pd.DataFrame([data])
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False, sep=";", encoding="utf-8-sig")
    else:
        df.to_csv(filename, mode="a", header=False, index=False, sep=";", encoding="utf-8-sig")

# ==================================================
# ÉTAPE 0 – ACCÈS SÉCURISÉ
# ==================================================
if st.session_state.step == 0:
    st.title("🔐 Accès au diagnostic ICI")
    email = st.text_input("Email professionnel")
    code = st.text_input("Code d’accès", type="password")

    if st.button("Accéder au questionnaire"):
        statut, personne = verifier_acces(email, code)

        if statut == "REFUSE":
            st.error("Accès refusé. Vérifiez vos informations.")
        elif statut == "DEJA_REPONDU":
            st.warning("Vous avez déjà répondu. Merci 🙏")
        else:
            st.session_state.invite = personne
            st.session_state.step = 1
            st.rerun()

# ==================================================
# ÉTAPE 1 – INTRODUCTION
# ==================================================
elif st.session_state.step == 1:
    st.markdown("## 🚀 Indice de Culture de l’Innovation (ICI)")
    st.write("Diagnostic rapide de la culture d’innovation.")
    if st.button("Démarrer"):
        st.session_state.step = 2
        st.session_state.current_q = 0
        st.session_state.responses = {}
        st.rerun()

# ==================================================
# ÉTAPE 2 – QUESTIONS
# ==================================================
elif st.session_state.step == 2:
    axe, q_id = questions_sequence[st.session_state.current_q]
    st.markdown(f"### 📍 {axe}")
    st.write(questions_text[q_id])

    st.session_state.responses[q_id] = st.select_slider(
        "Votre réponse",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: {
            1: "1 – Pas du tout d’accord",
            2: "2 – Pas d’accord",
            3: "3 – Neutre / NSP",
            4: "4 – D’accord",
            5: "5 – Tout à fait d’accord"
        }[x],
        key=q_id
    )

    st.progress(int((st.session_state.current_q + 1) / TOTAL_QUESTIONS * 100))

    if st.button("➡️ Suivant"):
        if st.session_state.current_q < TOTAL_QUESTIONS - 1:
            st.session_state.current_q += 1
        else:
            st.session_state.step = 3
        st.rerun()

# ==================================================
# ÉTAPE 3 – RÉSULTATS
# ==================================================
elif st.session_state.step == 3:
    r = st.session_state.responses

    scores = {
        "Audace": (r["Q1"] + r["Q2"] + r["Q3"]) / 3,
        "Curiosité": (r["Q4"] + r["Q5"] + r["Q6"]) / 3,
        "Agilité": (r["Q7"] + r["Q8"] + r["Q9"]) / 3,
        "Énergie": (r["Q10"] + r["Q11"] + r["Q12"]) / 3,
    }

    ici = (sum(scores.values()) / 4) * 20
    niveau, message = interpreter_score_ici(ici)

    marquer_comme_repondu(st.session_state.invite["email"])

    archiver_reponse({
        "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Utilisateur": st.session_state.invite["email"],
        "Score_ICI": round(ici, 2),
        **{k: round(v, 2) for k, v in scores.items()},
        **r
    })

    st.success("✅ Merci pour votre participation")
    st.metric("Indice ICI", f"{ici:.0f} / 100")
    st.markdown(f"### {niveau}")
    st.write(message)

    st.markdown("## 🔍 Analyse par axe")
    for axe, score in scores.items():
        st.write(f"**{axe}** : {score:.2f} / 5 — {analyse_par_axe(score)}")

    fig = go.Figure(
        data=go.Scatterpolar(
            r=list(scores.values()) + [list(scores.values())[0]],
            theta=list(scores.keys()) + [list(scores.keys())[0]],
            fill="toself"
        )
    )
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
