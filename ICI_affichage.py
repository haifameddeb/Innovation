import streamlit as st

# =========================
# INTERPRÉTATION ICI
# =========================
def interpret_ici(score: float) -> tuple:
    if score is None:
        return "—", "Aucune donnée disponible."

    if score < 2.5:
        return (
            "🔴 Faible",
            "La culture d’innovation est perçue comme peu favorable. "
            "Des leviers structurants peuvent être activés."
        )
    elif score < 3.5:
        return (
            "🟠 Moyen",
            "La dynamique d’innovation existe, mais reste hétérogène. "
            "Des pratiques gagnent à être consolidées."
        )
    else:
        return (
            "🟢 Avancé",
            "La culture d’innovation est globalement bien installée. "
            "Elle constitue un atout pour l’organisation."
        )


# =========================
# AFFICHAGE RÉSULTATS
# =========================
def afficher_resultats(resultats: dict):

    ici_global = resultats.get("ici_global")
    par_axe = resultats.get("par_axe", {})

    niveau, message = interpret_ici(ici_global)

    st.markdown("---")
    st.header("📊 Votre résultat InnoMeter")

    # =========================
    # SCORE GLOBAL
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Indice de Culture d’Innovation (ICI)",
            value=f"{ici_global}/5" if ici_global else "—"
        )

    with col2:
        st.markdown(f"### {niveau}")

    st.info(message)

    # =========================
    # SCORES PAR AXE
    # =========================
    if par_axe:
        st.subheader("🧭 Détail par axe")

        for axe, score in par_axe.items():
            st.progress(score / 5)
            st.caption(f"{axe} : {score}/5")

    # =========================
    # MESSAGE DE CONFIANCE
    # =========================
    st.markdown("""
    ---
    🔒 **Confidentialité**
    
    Vos réponses sont traitées de manière strictement anonyme.
    Les résultats sont analysés uniquement de façon collective.
    """)
