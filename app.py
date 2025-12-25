import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ================== CONFIG PAGE ==================
st.set_page_config(
    page_title="ICI Diagnostic",
    page_icon="🚀",
    layout="wide"
)

# ================== CONSTANTES ==================
LIKERT = {
    1: "Pas du tout d'accord",
    2: "Pas d'accord",
    3: "Neutre",
    4: "D'accord",
    5: "Tout à fait d'accord"
}

QUESTIONS = {
    "Audace": [
        "Si je tente une nouvelle approche et que ça ne marche pas, mon manager considère cela comme un apprentissage plutôt que comme une faute.",
        "Dans mon équipe, on encourage les idées un peu \"folles\" ou différentes.",
        "Je me sens à l'aise pour exprimer une opinion contraire à celle de mes supérieurs."
    ],
    "Curiosité": [
        "Nous prenons régulièrement le temps d'observer ce que font nos concurrents ou d'autres secteurs.",
        "Je crois que chaque collaborateur, quel que soit son poste, peut apporter une idée majeure au groupe.",
        "On nous incite à sortir de notre \"bulle\" pour rencontrer des collègues d'autres départements."
    ],
    "Agilité": [
        "Quand un problème survient, nous cherchons d'abord une solution plutôt qu'un coupable.",
        "Nous sommes capables de changer nos habitudes rapidement si une meilleure façon de faire est proposée.",
        "Ici, \"on a toujours fait comme ça\" est une phrase que l'on entend rarement."
    ],
    "Énergie": [
        "Si j'ai une idée, je sais vers qui me tourner pour m'aider à la tester.",
        "Mes collègues partagent volontiers leurs informations et leurs découvertes.",
        "Je sens que la direction croit vraiment en notre capacité à inventer le futur du groupe."
    ]
}

# ================== SESSION ==================
if "responses" not in st.session_state:
    st.session_state.responses = {}

# ================== UI ==================
st.title("🚀 ICI Diagnostic Culture Innovation")
st.markdown("### Questionnaires anonymes – Échelle de 1 à 5")

st.divider()

# ================== QUESTIONNAIRE ==================
for axe, questions in QUESTIONS.items():
    st.subheader(f"📌 Axe : {axe}")
    for i, q in enumerate(questions):
        key = f"{axe}_{i}"
        st.session_state.responses[key] = st.radio(
            q,
            options=list(LIKERT.keys()),
            format_func=lambda x: f"{x} - {LIKERT[x]}",
            horizontal=True,
            key=key
        )
    st.divider()

# ================== CALCUL ==================
def calcul_scores(responses):
    scores = {}
    for axe in QUESTIONS:
        vals = [
            responses[f"{axe}_{i}"]
            for i in range(3)
            if f"{axe}_{i}" in responses
        ]
        scores[axe] = sum(vals) / len(vals)
    ici = sum(scores.values()) / 4 * 20
    return scores, ici

# ================== VALIDATION ==================
if st.button("📊 Valider et afficher les résultats"):
    scores, ici = calcul_scores(st.session_state.responses)

    st.success("Questionnaire complété avec succès !")

    # Résumé
    st.subheader("📈 Résultats par axe")
    df = pd.DataFrame({
        "Axe": scores.keys(),
        "Score": scores.values()
    })

    fig = px.bar(
        df,
        x="Axe",
        y="Score",
        text="Score",
        range_y=[1, 5],
        title="Score moyen par axe"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🎯 Indice Culture Innovation (ICI)")
    st.metric("ICI Global", f"{ici:.1f} / 100")

    if ici < 50:
        st.error("Culture Prudente / Silotée – Transformation urgente")
    elif ici < 75:
        st.warning("Culture en Éveil – Bonnes bases mais blocages persistants")
    else:
        st.success("Culture Innovante – L'innovation est ancrée")

    # Export
    export_df = pd.DataFrame.from_dict(
        st.session_state.responses, orient="index", columns=["Réponse"]
    )
    export_df["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.download_button(
        "📥 Télécharger les réponses (Excel)",
        export_df.to_csv(index=True),
        file_name="ici_diagnostic_resultats.csv",
        mime="text/csv"
    )
