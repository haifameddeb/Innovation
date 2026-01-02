import pandas as pd

# =========================
# MAPPING RÉPONSES → SCORE
# =========================
SCORE_MAP = {
    "Pas du tout d’accord": 1,
    "Plutôt pas d’accord": 2,
    "Neutre": 3,
    "Plutôt d’accord": 4,
    "Tout à fait d’accord": 5
}

# =========================
# CALCUL ICI
# =========================
def calcul_ici(responses: list) -> dict:
    """
    responses = liste de dicts :
    {
        email,
        question,
        axe,
        reponse
    }
    """

    df = pd.DataFrame(responses)

    # Sécurité
    if df.empty:
        return {
            "ici_global": None,
            "par_axe": {}
        }

    # Conversion réponse → score
    df["score"] = df["reponse"].map(SCORE_MAP)

    # =========================
    # SCORE PAR AXE
    # =========================
    score_par_axe = (
        df
        .groupby("axe")["score"]
        .mean()
        .round(2)
        .to_dict()
    )

    # =========================
    # ICI GLOBAL
    # =========================
    ici_global = round(df["score"].mean(), 2)

    return {
        "ici_global": ici_global,
        "par_axe": score_par_axe
    }
