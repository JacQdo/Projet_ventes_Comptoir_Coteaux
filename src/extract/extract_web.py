"""Extraction et préparation des données Web."""

from pathlib import Path

import pandas as pd


# Chemins du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "Fichier_web.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "web_products.csv"

# Colonnes nécessaires pour l'analyse
EXPECTED_COLUMNS = [
    "sku",
    "total_sales",
    "post_type",
]


def extract_web() -> pd.DataFrame:
    """Lire et contrôler les données produits provenant du Web."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fichier Web introuvable : {INPUT_FILE}"
        )

    df = pd.read_excel(INPUT_FILE)

    # Vérification des colonnes
    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colonnes Web manquantes : {missing_columns}"
        )

    # Conserver uniquement les colonnes utiles
    df = df[EXPECTED_COLUMNS].copy()

    # Garder uniquement les produits WooCommerce
    df = df[df["post_type"] == "product"].copy()

    # Nettoyage du SKU
    df["sku"] = pd.to_numeric(
        df["sku"],
        errors="coerce",
    ).astype("Int64")

    # Nettoyage des ventes
    df["total_sales"] = pd.to_numeric(
        df["total_sales"],
        errors="coerce",
    )

    # Nettoyage du type
    df["post_type"] = (
        df["post_type"]
        .astype("string")
        .str.strip()
    )

    # Suppression des valeurs manquantes
    df = df.dropna(
        subset=["sku", "total_sales"]
    )

    # Suppression des doublons sur la clé Web
    if df["sku"].duplicated().any():
        duplicates = df.loc[
            df["sku"].duplicated(keep=False),
            "sku",
        ].tolist()

        raise ValueError(
            f"sku en doublon détecté(s) : {duplicates}"
        )

    # Contrôle des ventes négatives
    if (df["total_sales"] < 0).any():
        negative_sales = df.loc[
            df["total_sales"] < 0,
            ["sku", "total_sales"],
        ].to_dict("records")

        raise ValueError(
            "Des ventes négatives sont présentes dans le Web : "
            f"{negative_sales}"
        )

    return df


def save_web(df: pd.DataFrame) -> None:
    """Enregistrer les données Web préparées."""
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Fichier généré : {OUTPUT_FILE}")
    print(f"Nombre de produits Web : {len(df)}")


def main() -> None:
    """Exécuter l'extraction Web."""
    df = extract_web()
    save_web(df)


if __name__ == "__main__":
    main()