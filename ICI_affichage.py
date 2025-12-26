import streamlit as st
import plotly.graph_objects as go

# =========================
# INTERPRÉTATION ICI
# =========================
def interpret_ici(score: float):
    if score < 2.5:
        return "🔴 Faible", "La culture d’innovation est perçue comme peu favorable."
    elif score < 3.5:
        return "🟠 Moyen", "La dynamique d’innovation existe mais reste perfectible."
    else:
        return "🟢 Avancé", "La culture d’innovation est bien installée."


# =========================
# RADAR DES AXES
# =========================
def radar_axes(scores_par_axe: dict):
    """
    scores_par_axe = {
        "Culture": 3.8,
        "Organisation": 3.2,
        "Technologie": 4.1,
        "Leadership": 3.5
    }
    """

    axes = list(scores_par_axe.keys())
    scores = list(scores_par_axe.values())

    # Fermeture du polygone
    axes.append(axes[0])
    scores.append(scores[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=axes,
        fill='toself',
        fillcolor='rgba(79, 112, 255, 0.4)',  # bleu InnoMeter
        line=dict(color='rgba(79, 112, 255, 1)', width=2),
        name="Indice par axe"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5]
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig


# =========================
# AFFICHAGE RÉSULTATS
# =========================
def afficher_resultats(resultats: dict):

    ici = resultats.get("ici_global")
    par_axe = resultats.get("par_axe", {})

    niveau, message = interpret_ici(ici)

    st.header("📊 Votre résultat InnoMeter")

    # =========================
    # SCORE GLOBAL
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Indice de Culture d’Innovation (ICI)",
            f"{ici}/5"
        )

    with col2:
        st.markdown(f"### {niveau}")

    st.info(message)

    # =========================
    # VISUEL RADAR
    # =========================
    if par_axe:
        st.subheader("🧭 Lecture par axe")

        fig = radar_axes(par_axe)
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # MESSAGE DE CONFIANCE
    # =========================
    st.markdown("""
    ---
    🔒 **Confidentialité**
    
    Vos réponses sont traitées de manière strictement anonyme  
    et analysées uniquement de façon collective.
    """)
