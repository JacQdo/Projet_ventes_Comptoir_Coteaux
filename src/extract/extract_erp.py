
"""Extraction et préparation des données ERP."""

from pathlib import Path

import pandas as pd


# Chemins du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "Fichier_ERP.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "erp_products.csv"

# Colonnes attendues dans l'ERP
EXPECTED_COLUMNS = [
    "product_id",
    "onsale_web",
    "price",
    "stock_quantity",
    "stock_status",
]


def extract_erp() -> pd.DataFrame:
    """Lire, nettoyer et contrôler les données ERP."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fichier ERP introuvable : {INPUT_FILE}"
        )

    # Lecture du fichier Excel
    df = pd.read_excel(INPUT_FILE)

    # Vérification des colonnes
    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colonnes ERP manquantes : {missing_columns}"
        )

    # Conservation des colonnes utiles
    df = df[EXPECTED_COLUMNS].copy()

    # Conversion des types
    df["product_id"] = pd.to_numeric(
        df["product_id"],
        errors="coerce",
    ).astype("Int64")

    df["onsale_web"] = pd.to_numeric(
        df["onsale_web"],
        errors="coerce",
    ).astype("Int64")

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce",
    )

    df["stock_quantity"] = pd.to_numeric(
        df["stock_quantity"],
        errors="coerce",
    ).astype("Int64")

    df["stock_status"] = (
        df["stock_status"]
        .astype("string")
        .str.strip()
    )

    # ---------------------------------------------------------
    # 1. Suppression des valeurs manquantes
    # ---------------------------------------------------------

    before_missing = len(df)

    df = df.dropna(
        subset=[
            "product_id",
            "price",
            "stock_quantity",
        ]
    ).copy()

    removed_missing = before_missing - len(df)

    # ---------------------------------------------------------
    # 2. Suppression des doublons
    # ---------------------------------------------------------

    duplicate_ids = df.loc[
        df["product_id"].duplicated(keep=False),
        "product_id",
    ].tolist()

    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=["product_id"],
        keep="first",
    ).copy()

    removed_duplicates = before_duplicates - len(df)

    # ---------------------------------------------------------
    # 3. Contrôle des prix négatifs
    # ---------------------------------------------------------

    negative_prices = df.loc[
        df["price"] < 0,
        [
            "product_id",
            "price",
        ],
    ]

    # ---------------------------------------------------------
    # 4. Contrôle des stocks négatifs
    # ---------------------------------------------------------

    negative_stock = df.loc[
        df["stock_quantity"] < 0,
        [
            "product_id",
            "stock_quantity",
        ],
    ]

    # ---------------------------------------------------------
    # 5. Contrôles qualité
    # ---------------------------------------------------------

    print("=== Contrôle qualité ERP ===")
    print(
        f"Lignes après suppression des valeurs manquantes : "
        f"{len(df)}"
    )
    print(
        f"Lignes supprimées pour valeurs manquantes : "
        f"{removed_missing}"
    )
    print(
        f"Doublons product_id supprimés : "
        f"{removed_duplicates}"
    )

    if duplicate_ids:
        print(
            "product_id en doublon détecté(s) : "
            f"{sorted(set(duplicate_ids))}"
        )
    else:
        print("Doublons product_id : aucun")

    if not negative_prices.empty:
        print(
            "ATTENTION : prix négatifs conservés dans les données :"
        )
        print(
            negative_prices.to_string(index=False)
        )
    else:
        print("Prix négatifs : aucun")

    if not negative_stock.empty:
        print(
            "ATTENTION : quantités de stock négatives "
            "conservées dans les données :"
        )
        print(
            negative_stock.to_string(index=False)
        )
    else:
        print("Stocks négatifs : aucun")

    # ---------------------------------------------------------
    # 6. Vérification finale de la clé primaire
    # ---------------------------------------------------------

    if df["product_id"].duplicated().any():
        raise ValueError(
            "La clé product_id n'est pas unique après nettoyage."
        )

    return df


def save_erp(df: pd.DataFrame) -> None:
    """Enregistrer les données ERP préparées."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Fichier généré : {OUTPUT_FILE}")
    print(f"Nombre de produits ERP : {len(df)}")


def main() -> None:
    """Exécuter l'extraction ERP."""

    df = extract_erp()
    save_erp(df)


if __name__ == "__main__":
    main()
