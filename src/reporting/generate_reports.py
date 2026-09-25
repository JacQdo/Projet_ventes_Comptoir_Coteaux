"""Génération des livrables commerciaux."""

from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Chemins
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sales_products.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "output"
)

CA_FILE = OUTPUT_DIR / "rapport_ca.xlsx"
PREMIUM_FILE = OUTPUT_DIR / "vins_premium.csv"
ORDINARY_FILE = OUTPUT_DIR / "vins_ordinaires.csv"


# -------------------------------------------------------------------
# Colonnes
# -------------------------------------------------------------------

REPORT_COLUMNS = [
    "product_id",
    "id_web",
    "sku",
    "price",
    "total_sales",
    "ca",
]


# -------------------------------------------------------------------
# Lecture
# -------------------------------------------------------------------

def load_sales() -> pd.DataFrame:
    """Charger les données commerciales transformées."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "product_id",
        "id_web",
        "sku",
        "price",
        "total_sales",
        "ca",
        "premium",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {missing_columns}"
        )

    return df


# -------------------------------------------------------------------
# Rapport CA
# -------------------------------------------------------------------

def generate_ca_report(df: pd.DataFrame) -> None:
    """Générer le rapport Excel du chiffre d'affaires."""

    report = df[REPORT_COLUMNS].copy()

    ca_total = report["ca"].sum()

    total_row = pd.DataFrame(
        [
            {
                "product_id": "",
                "id_web": "",
                "sku": "",
                "price": "",
                "total_sales": "TOTAL",
                "ca": ca_total,
            }
        ]
    )

    report = pd.concat(
        [report, total_row],
        ignore_index=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report.to_excel(
        CA_FILE,
        index=False,
        sheet_name="Chiffre_Affaires",
    )

    print(f"Rapport CA généré : {CA_FILE}")
    print(f"CA total : {ca_total:.2f} €")


# -------------------------------------------------------------------
# Listes Premium / Ordinaires
# -------------------------------------------------------------------

def generate_wine_lists(df: pd.DataFrame) -> None:
    """Générer les listes Premium et Ordinaires."""

    wine_columns = [
        "product_id",
        "id_web",
        "sku",
        "price",
        "total_sales",
        "ca",
        "price_zscore",
        "premium",
    ]

    premium = df.loc[
        df["premium"] == True,
        wine_columns,
    ].copy()

    ordinary = df.loc[
        df["premium"] == False,
        wine_columns,
    ].copy()

    premium = premium.sort_values(
        "price",
        ascending=False,
    )

    ordinary = ordinary.sort_values(
        "price",
        ascending=False,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    premium.to_csv(
        PREMIUM_FILE,
        index=False,
    )

    ordinary.to_csv(
        ORDINARY_FILE,
        index=False,
    )

    print(
        f"Liste Premium générée : {PREMIUM_FILE}"
    )
    print(
        f"Nombre de vins premium : {len(premium)}"
    )

    print(
        f"Liste Ordinaire générée : {ORDINARY_FILE}"
    )
    print(
        f"Nombre de vins ordinaires : {len(ordinary)}"
    )


# -------------------------------------------------------------------
# Programme principal
# -------------------------------------------------------------------

def main() -> None:
    """Générer les trois livrables commerciaux."""

    print("=== Génération des livrables ===")

    df = load_sales()

    print(
        f"Produits chargés : {len(df)}"
    )

    print("\n=== Rapport chiffre d'affaires ===")

    generate_ca_report(df)

    print("\n=== Listes des vins ===")

    generate_wine_lists(df)

    print("\n=== Génération terminée ===")


if __name__ == "__main__":
    main()