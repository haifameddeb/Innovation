import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================
# CONFIG
# =========================
QUESTIONS_FILE = "questions_ici.xlsx"
RESULTATS_FILE = "resultats_innovation.csv"

# =========================
# UTILS
# =========================
def clean_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def load_questions():
    df_q = pd.read_excel(QUESTIONS_FILE, sheet_name="questions")
    df_q = clean_columns(df_q)

    required = {"axe", "code", "question"}
    if not required.issubset(df_q.columns):
        st.error("❌ Colonnes manquantes dans l’onglet questions")
        st.stop()

    return df_q

# =========================
# PAGE QUESTIONNAIRE
# =========================
def page_questionnaire():

    # 🔒 Sécurité : accès uniquement après auth
    if "user" not in st.session_state:
        st.error("Accès non autorisé.")
        st.stop()

    # =========================
    # INIT SESSION
    # =========================
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    # =========================
    # LOAD QUESTIONS
    # =========================
    df_q = load_questions()
    questions = df_q.to_dict("records")

    # Séquence par axe (pour le calcul)
    axes_data = {
        axe: df_q[df_q["axe"] == axe]["code"].tolist()
        for axe in df_q["axe"].unique()
    }

    # =========================
    # FIN DU QUESTIONNAIRE
    # =========================
    if st.session_state.q_index >= len(questions):
        _finaliser_questionnaire(axes_data)
        return

    # =========================
    # QUESTION COURANTE
    # =========================
    q = questions[st.session_state.q_index]

    st.subheader(f"Axe : {q['axe']}")
    st.write(q["question"])

    valeur = st.select_slider(
        "Votre réponse",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: [
            "Pas du tout d’accord",
            "Pas d’accord",
            "Neutre",
            "D’accord",
            "Tout à fait d’accord"
        ][x - 1],
        key=f"q_{q['code']}"
    )

    st.session_state.responses[q["code"]] = valeur

    # =========================
    # PROGRESSION
    # =========================
    st.progress((st.session_state.q_index + 1) / len(questions))
    st.caption(f"Question {st.session_state.q_index + 1} / {len(questions)}")

    # =========================
    # NAVIGATION
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.q_index > 0:
            if st.button("⬅ Précédent"):
                st.session_state.q_index -= 1
                st.rerun()

    with col2:
        if st.button("Suivant ➡"):
            st.session_state.q_index += 1
            st.rerun()

# =========================
# FINALISATION & SAUVEGARDE
# =========================
def _finaliser_questionnaire(axes_data):

    st.subheader("✅ Merci pour votre participation")

    r = st.session_state.responses

    # --- Score par axe
    scores_axes = {
        axe: round(sum(r[q] for q in qs) / len(qs), 2)
        for axe, qs in axes_data.items()
    }

    # --- Calcul ICI (score /5 → /100)
    ici = round(sum(scores_axes.values()) / len(scores_axes) * 20, 1)

    # --- Résultat
    st.metric("Indice de Culture d’Innovation (ICI)", f"{ici} / 100")

    # =========================
    # SAUVEGARDE
    # =========================
    df_out = pd.DataFrame([{
        "email": st.session_state.user["email"],
        "filiale": st.session_state.user["filiale"],
        **r,
        **scores_axes,
        "ici": ici,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    }])

    if os.path.exists(RESULTATS_FILE):
        df_out.to_csv(
            RESULTATS_FILE,
            mode="a",
            header=False,
            index=False,
            sep=";"
        )
    else:
        df_out.to_csv(
            RESULTATS_FILE,
            index=False,
            sep=";"
        )

    st.success("Vos réponses ont été enregistrées avec succès.")

    if st.button("🏁 Terminer"):
        # Nettoyage session questionnaire
        del st.session_state.q_index
        del st.session_state.responses

        st.session_state.step = 0
        st.rerun()
