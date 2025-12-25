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
INVITES_FILE = "invites.csv"
RESULTATS_FILE = "resultats_innovation.csv"
QUESTIONS_FILE = "questions_ici.xlsx"

st.set_page_config(
    page_title="Indice de Culture de l’Innovation (ICI)",
    layout="wide"
)

# ==================================================
# CHARGEMENT DES QUESTIONS & INTERPRÉTATION
# ==================================================
if not os.path.exists(QUESTIONS_FILE):
    st.error(f"❌ Fichier introuvable : {QUESTIONS_FILE}")
    st.stop()

df_questions = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
df_interp = pd.read_excel(QUESTIONS_FILE, sheet_name="interpretation")

axes_data = {
    axe: df_questions[df_questions["axe"] == axe]["code"].tolist()
    for axe in df_questions["axe"].unique()
}

questions_sequence = df_questions.to_dict("records")

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
# FONCTIONS UTILITAIRES
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

def archiver_resultats(data):
    df = pd.DataFrame([data])
    if not os.path.exists(RESULTATS_FILE):
        df.to_csv(RESULTATS_FILE, index=False)
    else:
        df.to_csv(RESULTATS_FILE, mode="a", header=False, index=False)

def determiner_maturite(score):
    ligne = df_interp[(df_interp["min"] <= score) & (score <= df_interp["max"])]
    if not ligne.empty:
        return ligne.iloc[0]["niveau"], ligne.iloc[0]["message"]
    return "Non évalué", ""

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
            elif personne["statut"] == "OUI":
                st.warning("Vous avez déjà répondu.")
            else:
                st.session_state.step = 1
            st.rerun()
        else:
            st.error("Accès refusé")

# ==================================================
# STEP 1 – QUESTIONNAIRE
# ==================================================
elif st.session_state.step == 1:
    q = questions_sequence[st.session_state.current_q]

    st.subheader(f"Axe : {q['axe']}")
    st.write(q["question"])

    st.session_state.responses[q["code"]] = st.select_slider(
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

    st.progress((st.session_state.current_q + 1) / len(questions_sequence))

    if st.button("Suivant"):
        if st.session_state.current_q < len(questions_sequence) - 1:
            st.session_state.current_q += 1
        else:
            st.session_state.step = 2
        st.rerun()

# ==================================================
# STEP 2 – RÉSULTATS UTILISATEUR
# ==================================================
elif st.session_state.step == 2:
    r = st.session_state.responses

    scores_axes = {
        axe: sum(r[q] for q in qs) / len(qs)
        for axe, qs in axes_data.items()
    }

    ici = sum(scores_axes.values()) / len(scores_axes) * 20
    niveau, message = determiner_maturite(ici)

    marquer_repondu(st.session_state.invite["email"])
    archiver_resultats({
        "email": st.session_state.invite["email"],
        "filiale": st.session_state.invite["filiale"],
        **scores_axes,
        "ICI": round(ici, 2),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    st.success(f"Score ICI : {ici:.0f}/100")
    st.info(f"{niveau} — {message}")

    fig = go.Figure(go.Scatterpolar(
        r=list(scores_axes.values()) + [list(scores_axes.values())[0]],
        theta=list(scores_axes.keys()) + [list(scores_axes.keys())[0]],
        fill="toself"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,5])))
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Retour à l’authentification"):
        st.session_state.clear()
        st.rerun()

# ==================================================
# STEP 99 – DASHBOARD ADMIN (ROBUSTE)
# ==================================================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Administrateur – ICI")

    df_inv = pd.read_csv(INVITES_FILE)

    # 🔐 Lecture sécurisée des résultats (CORRECTION DÉFINITIVE)
    if os.path.exists(RESULTATS_FILE) and os.path.getsize(RESULTATS_FILE) > 0:
        try:
            df_res = pd.read_csv(RESULTATS_FILE)
        except pd.errors.EmptyDataError:
            df_res = pd.DataFrame()
    else:
        df_res = pd.DataFrame()

    # ==================================================
    # KPI GLOBAUX
    # ==================================================
    total_inv = len(df_inv)
    total_rep = len(df_inv[df_inv["statut"] == "OUI"])
    taux = round((total_rep / total_inv) * 100, 1) if total_inv else 0

    ici_moy = round(df_res["ICI"].mean(), 1) if not df_res.empty else 0
    niveau_groupe, _ = determiner_maturite(ici_moy) if ici_moy > 0 else ("Non évalué", "")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("ICI moyen Groupe", ici_moy)
    col2.metric("Maturité Groupe", niveau_groupe)
    col3.metric("Taux participation", f"{taux}%")
    col4.metric("Répondants", total_rep)
    col5.metric("Filiales", df_inv["filiale"].nunique())

    st.divider()

    # ==================================================
    # KPI PAR FILIALE
    # ==================================================
    st.subheader("🏢 KPI par filiale")

    if not df_res.empty:
        df_merge = df_res.merge(
            df_inv[["email", "filiale"]],
            on="email",
            how="left"
        )

        kpi_filiale = (
            df_merge.groupby("filiale")["ICI"]
            .agg(["mean", "min", "max", "std", "count"])
            .reset_index()
        )

        kpi_filiale.columns = [
            "Filiale", "ICI moyen", "ICI min", "ICI max", "Dispersion", "Réponses"
        ]

        invites_fil = (
            df_inv.groupby("filiale")
            .size()
            .reset_index(name="Invités")
        )

        kpi_filiale = kpi_filiale.merge(invites_fil, on="Filiale")
        kpi_filiale["Taux %"] = round(
            (kpi_filiale["Réponses"] / kpi_filiale["Invités"]) * 100, 1
        )

        kpi_filiale["Maturité"] = kpi_filiale["ICI moyen"].apply(
            lambda x: determiner_maturite(x)[0]
        )

        st.dataframe(kpi_filiale, use_container_width=True)

        fig = px.bar(
            kpi_filiale,
            x="Filiale",
            y="ICI moyen",
            color="Maturité",
            text="ICI moyen",
            range_y=[0, 100],
            title="Indice ICI moyen par filiale"
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("ℹ️ Aucune donnée de réponse disponible pour le moment.")

    if st.button("⬅️ Déconnexion"):
        st.session_state.clear()
        st.rerun()
