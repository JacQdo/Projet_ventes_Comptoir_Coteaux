
"""Fusion des données ERP et Web et calcul des indicateurs de vente."""

from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Chemins du projet
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ERP_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "erp_products.csv"
)

LIAISON_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "liaison_products.csv"
)

WEB_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "web_products.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sales_products.csv"
)


# -------------------------------------------------------------------
# Lecture des fichiers
# -------------------------------------------------------------------

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Charger les trois fichiers préparés."""

    for file_path in [ERP_FILE, LIAISON_FILE, WEB_FILE]:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Fichier introuvable : {file_path}"
            )

    erp = pd.read_csv(ERP_FILE)
    liaison = pd.read_csv(LIAISON_FILE)
    web = pd.read_csv(WEB_FILE)

    return erp, liaison, web


# -------------------------------------------------------------------
# Fusion des données
# -------------------------------------------------------------------

def merge_data(
    erp: pd.DataFrame,
    liaison: pd.DataFrame,
    web: pd.DataFrame,
) -> pd.DataFrame:
    """Fusionner ERP, table de liaison et données Web."""

    # ---------------------------------------------------------------
    # Jointure ERP → liaison
    # ---------------------------------------------------------------

    merged = erp.merge(
        liaison,
        on="product_id",
        how="inner",
        validate="one_to_one",
    )

    print(
        f"Produits après jointure ERP → liaison : {len(merged)}"
    )

    # ---------------------------------------------------------------
    # Jointure liaison → Web
    #
    # liaison.id_web correspond à web.sku
    # ---------------------------------------------------------------

    merged = merged.merge(
        web,
        left_on="id_web",
        right_on="sku",
        how="inner",
        validate="one_to_one",
    )

    print(
        f"Produits après jointure avec le Web : {len(merged)}"
    )

    return merged


# -------------------------------------------------------------------
# Calcul du chiffre d'affaires
# -------------------------------------------------------------------

def calculate_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calculer le chiffre d'affaires par produit."""

    df = df.copy()

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce",
    )

    df["total_sales"] = pd.to_numeric(
        df["total_sales"],
        errors="coerce",
    )

    # CA = prix unitaire × nombre de ventes
    df["ca"] = df["price"] * df["total_sales"]

    return df


# -------------------------------------------------------------------
# Classification des vins premium
# -------------------------------------------------------------------

def classify_premium(df: pd.DataFrame) -> pd.DataFrame:
    """Calculer le z-score du prix et identifier les vins premium."""

    df = df.copy()

    mean_price = df["price"].mean()
    std_price = df["price"].std()

    if std_price == 0 or pd.isna(std_price):
        raise ValueError(
            "Impossible de calculer le z-score : "
            "écart-type du prix nul ou manquant."
        )

    # Formule :
    # z = (prix - moyenne) / écart-type
    df["price_zscore"] = (
        (df["price"] - mean_price)
        / std_price
    )

    # Premium si z-score > 2
    df["premium"] = df["price_zscore"] > 2

    return df


# -------------------------------------------------------------------
# Sauvegarde
# -------------------------------------------------------------------

def save_sales(df: pd.DataFrame) -> None:
    """Enregistrer les données transformées."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"Fichier généré : {OUTPUT_FILE}"
    )

    print(
        f"Nombre de produits fusionnés : {len(df)}"
    )


# -------------------------------------------------------------------
# Programme principal
# -------------------------------------------------------------------

def main() -> None:
    """Exécuter la transformation complète."""

    print("=== Chargement des données ===")

    erp, liaison, web = load_data()

    print(
        f"ERP : {len(erp)} lignes"
    )

    print(
        f"Liaison : {len(liaison)} lignes"
    )

    print(
        f"Web : {len(web)} lignes"
    )

    print("\n=== Jointure des données ===")

    df = merge_data(
        erp,
        liaison,
        web,
    )

    print("\n=== Calcul du chiffre d'affaires ===")

    df = calculate_revenue(df)

    ca_total = df["ca"].sum()

    print(
        f"Chiffre d'affaires total : {ca_total:.2f} €"
    )

    print("\n=== Classification premium ===")

    df = classify_premium(df)

    premium_count = int(
        df["premium"].sum()
    )

    print(
        f"Nombre de vins premium : {premium_count}"
    )

    print(
        f"Nombre de vins ordinaires : "
        f"{len(df) - premium_count}"
    )

    print("\n=== Sauvegarde ===")

    save_sales(df)


if __name__ == "__main__":
    main()
