import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

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

    axes = list(scores_par_axe.keys())
    scores = list(scores_par_axe.values())

    axes.append(axes[0])
    scores.append(scores[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=axes,
        fill='toself',
        fillcolor='rgba(79, 112, 255, 0.4)',
        line=dict(color='rgba(79, 112, 255, 1)', width=2)
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
        margin=dict(l=30, r=30, t=30, b=30)
    )

    return fig


# =========================
# HISTOGRAMME PAR AXE
# =========================
def histogram_axes(scores_par_axe: dict):

    df = {
        "Axe": list(scores_par_axe.keys()),
        "Score": list(scores_par_axe.values())
    }

    fig = px.bar(
        df,
        x="Axe",
        y="Score",
        range_y=[0, 5],
        text="Score"
    )

    fig.update_traces(
        marker_color="rgba(79, 112, 255, 0.8)",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="Score",
        xaxis_title="",
        margin=dict(l=30, r=30, t=30, b=30)
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

    colA, colB = st.columns(2)

    with colA:
        st.metric(
            "Indice de Culture d’Innovation (ICI)",
            f"{ici}/5"
        )

    with colB:
        st.markdown(f"### {niveau}")

    st.info(message)

    # =========================
    # VISUELS CÔTE À CÔTE
    # =========================
    if par_axe:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧭 Lecture globale par axe")
            st.plotly_chart(
                radar_axes(par_axe),
                use_container_width=True
            )

        with col2:
            st.subheader("📊 Détail des scores")
            st.plotly_chart(
                histogram_axes(par_axe),
                use_container_width=True
            )

    # =========================
    # MESSAGE DE CONFIANCE
    # =========================
    st.markdown("""
    ---
    🔒 **Confidentialité**
    
    Vos réponses sont traitées de manière strictement anonyme  
    et analysées uniquement de façon collective.
    """)
