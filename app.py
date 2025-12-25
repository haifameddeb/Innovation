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

# ==================================================
# STYLE
# ==================================================
st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #0f172a, #020617);
    padding: 16px 24px;
    border-radius: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
    margin-bottom: 40px;
}
.hero {
    text-align: center;
    margin-bottom: 30px;
}
.hero h1 {
    font-size: 34px;
    font-weight: 800;
}
.hero p {
    color: #6b7280;
}
.kpis {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 30px 0;
}
.kpi {
    background: #f8fafc;
    padding: 20px 30px;
    border-radius: 16px;
    text-align: center;
    min-width: 160px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #6366f1;
}
.cta {
    background: linear-gradient(90deg, #6366f1, #4f46e5);
    color: white;
    padding: 16px;
    border-radius: 14px;
    font-size: 18px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# SESSION
# ==================================================
if "step" not in st.session_state:
    st.session_state.step = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}

# ==================================================
# QUESTIONS
# ==================================================
axes_data = {
    "Audace": ["Q1", "Q2", "Q3"],
    "Curiosité": ["Q4", "Q5", "Q6"],
    "Agilité": ["Q7", "Q8", "Q9"],
    "Énergie": ["Q10", "Q11", "Q12"]
}

questions_text = {
    "Q1": "Si je tente une nouvelle approche et que ça ne marche pas, c’est vu comme un apprentissage.",
    "Q2": "Les idées originales sont encouragées.",
    "Q3": "Je peux exprimer un avis différent.",
    "Q4": "Nous observons nos concurrents.",
    "Q5": "Chacun peut apporter une idée majeure.",
    "Q6": "Les échanges inter-équipes sont encouragés.",
    "Q7": "On cherche une solution avant un responsable.",
    "Q8": "Nous savons changer rapidement.",
    "Q9": "« On a toujours fait comme ça » est rare.",
    "Q10": "Je sais comment tester une idée.",
    "Q11": "L’information circule librement.",
    "Q12": "La direction croit en l’innovation."
}

questions_sequence = [(axe, q) for axe in axes_data for q in axes_data[axe]]

# ==================================================
# FONCTIONS
# ==================================================
def verifier_acces(email, code):
    with open("invites.csv", encoding="utf-8") as f:
        for p in csv.DictReader(f):
            if p["email"].lower() == email.lower() and p["code"] == code:
                if p["admin"] == "OUI":
                    return "ADMIN", p
                if p["statut"] == "OUI":
                    return "DEJA", p
                return "OK", p
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
# STEP 0 – LANDING
# ==================================================
if st.session_state.step == 0:

    st.markdown("""
    <div class="header">
        <div>⚡ L’ÉCHO – Innovation Hub</div>
        <div>📊 Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <h1>Comment respire notre culture ?</h1>
        <p>Baromètre anonyme pour mesurer l’indice de culture d’innovation (ICI)</p>
    </div>
    """, unsafe_allow_html=True)

    df_inv = pd.read_csv("invites.csv")
    nb = len(df_inv[df_inv.statut == "OUI"])

    score = "--"
    if os.path.exists("resultats_innovation.csv"):
        score = round(pd.read_csv("resultats_innovation.csv")["ICI"].mean())

    st.markdown(f"""
    <div class="kpis">
        <div class="kpi"><div class="kpi-value">{nb}</div>RÉPONSES</div>
        <div class="kpi"><div class="kpi-value">{score}</div>SCORE GROUPE</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login"):
        email = st.text_input("Adresse email")
        code = st.text_input("Mot de passe", type="password")
        ok = st.form_submit_button("🚀 Démarrer le test")

        if ok:
            statut, p = verifier_acces(email, code)
            if statut == "ADMIN":
                st.info("🛡️ Accès administrateur")
                st.session_state.step = 99
                st.rerun()
            elif statut == "OK":
                st.session_state.invite = p
                st.session_state.step = 1
                st.rerun()
            elif statut == "DEJA":
                st.warning("Vous avez déjà répondu.")
            else:
                st.error("Accès refusé.")

# ==================================================
# STEP 1 – QUESTIONNAIRE
# ==================================================
elif st.session_state.step == 1:
    axe, q = questions_sequence[st.session_state.current_q]
    st.subheader(f"Axe : {axe}")
    st.write(questions_text[q])

    st.session_state.responses[q] = st.radio(
        "Votre réponse",
        [1,2,3,4,5],
        format_func=lambda x: ["Pas du tout d’accord","Pas d’accord","Neutre","D’accord","Tout à fait d’accord"][x-1]
    )

    st.progress((st.session_state.current_q+1)/len(questions_sequence))

    if st.button("Suivant"):
        if st.session_state.current_q < len(questions_sequence)-1:
            st.session_state.current_q += 1
        else:
            st.session_state.step = 2
        st.rerun()

# ==================================================
# STEP 2 – RÉSULTATS
# ==================================================
elif st.session_state.step == 2:
    r = st.session_state.responses
    scores = {axe: sum(r[q] for q in qs)/3 for axe, qs in axes_data.items()}
    ici = sum(scores.values())/4*20

    marquer_repondu(st.session_state.invite["email"])
    archiver({"email": st.session_state.invite["email"], **r, **scores, "ICI": ici})

    st.success(f"Score ICI : {ici:.0f}/100")

    fig = go.Figure(go.Scatterpolar(
        r=list(scores.values())+[list(scores.values())[0]],
        theta=list(scores.keys())+[list(scores.keys())[0]],
        fill='toself'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,5])))
    st.plotly_chart(fig)

# ==================================================
# STEP 99 – DASHBOARD ADMIN
# ==================================================
elif st.session_state.step == 99:
    st.title("📊 Dashboard Admin")

    df_inv = pd.read_csv("invites.csv")
    df_res = pd.read_csv("resultats_innovation.csv") if os.path.exists("resultats_innovation.csv") else pd.DataFrame()

    st.dataframe(df_inv, use_container_width=True)

    if not df_res.empty:
        st.subheader("📊 Moyennes par axe")
        st.bar_chart(df_res[list(axes_data.keys())])

    st.download_button("⬇️ Export invités", df_inv.to_csv(index=False), "invites.csv")
    if not df_res.empty:
        st.download_button("⬇️ Export résultats", df_res.to_csv(index=False), "resultats.csv")

    if st.button("⬅️ Retour"):
        st.session_state.step = 0
        st.rerun()
