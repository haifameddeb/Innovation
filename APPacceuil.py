import streamlit as st

# =========================
# CONFIG PAGE
# =========================
st.set_page_config(
    page_title="InnoMeter – Accès",
    page_icon="🔵",
    layout="centered"
)

# =========================
# HEADER
# =========================
st.markdown("<br>", unsafe_allow_html=True)

st.title("🔵 InnoMeter")
st.subheader("Le baromètre de la culture d’innovation")

st.markdown("""
<p style="font-size:16px; color:#555;">
Comment respire notre culture d’innovation ?<br>
Participez au baromètre <b>InnoMeter</b> pour mesurer l’indice de culture
d’innovation (ICI) de notre organisation.
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# FORMULAIRE DE CONNEXION
# =========================
with st.container():
    email = st.text_input("📧 Email professionnel")
    password = st.text_input("🔑 Mot de passe", type="password")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Démarrer le diagnostic", use_container_width=True):
        # 👉 Ici tu branches TA logique d’authentification existante
        st.success("Authentification en cours…")

# =========================
# CITATION & CONFIANCE
# =========================
st.markdown("""
<div style="text-align:center; margin-top:40px; font-style:italic; color:#666;">
    « On n’améliore durablement que ce que l’on prend le temps de mesurer. »
</div>

<div style="text-align:center; margin-top:10px; font-size:12px; color:#888;">
    🔒 Vos réponses sont anonymes et utilisées uniquement à des fins d’analyse collective.
</div>
""", unsafe_allow_html=True)
