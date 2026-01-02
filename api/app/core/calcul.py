import pandas as pd
from typing import List, Dict, Any

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
# CALCUL ICI (LOGIQUE MÉTIER PURE)
# =========================
def calcul_ici(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    responses : liste de dictionnaires de la forme :
    {
        "email": str,
        "question": str,
        "axe": str,
        "reponse": str
    }

    Retour :
    {
        "ici_global": float | None,
        "par_axe": {
            axe: score_moyen
        }
    }
    """

    # Création du DataFrame
    df = pd.DataFrame(responses)

    # Sécurité : aucune donnée
    if df.empty:
        return {
            "ici_global": None,
            "par_axe": {}
        }

    # Sécurité : colonnes obligatoires
    colonnes_obligatoires = {"axe", "reponse"}
    if not colonnes_obligatoires.issubset(df.columns):
        raise ValueError(
            f"Colonnes manquantes. Requis : {colonnes_obligatoires}"
        )

    # Conversion réponse → score
    df["score"] = df["reponse"].map(SCORE_MAP)

    # Sécurité : réponses non reconnues
    if df["score"].isnull().any():
        valeurs_invalides = df[df["score"].isnull()]["reponse"].unique().tolist()
        raise ValueError(
            f"Réponses non reconnues dans SCORE_MAP : {valeurs_invalides}"
        )

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
