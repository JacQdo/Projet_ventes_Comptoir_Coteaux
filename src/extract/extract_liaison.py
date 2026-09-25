
"""Extraction et préparation de la table de liaison ERP-Web."""

from pathlib import Path

import pandas as pd


# Chemins du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "fichier_liaison.xlsx"
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "liaison_products.csv"
)

# Colonnes attendues
EXPECTED_COLUMNS = [
    "product_id",
    "id_web",
]


def extract_liaison() -> pd.DataFrame:
    """Lire, nettoyer et contrôler la table de liaison."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fichier de liaison introuvable : {INPUT_FILE}"
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
            f"Colonnes de liaison manquantes : {missing_columns}"
        )

    # Conservation des colonnes utiles
    df = df[EXPECTED_COLUMNS].copy()

    # Conversion des types
    df["product_id"] = pd.to_numeric(
        df["product_id"],
        errors="coerce",
    ).astype("Int64")

    df["id_web"] = pd.to_numeric(
        df["id_web"],
        errors="coerce",
    ).astype("Int64")

    # ---------------------------------------------------------
    # 1. Suppression des valeurs manquantes
    # ---------------------------------------------------------

    before_missing = len(df)

    df = df.dropna(
        subset=[
            "product_id",
            "id_web",
        ]
    ).copy()

    removed_missing = before_missing - len(df)

    # ---------------------------------------------------------
    # 2. Recherche des doublons
    # ---------------------------------------------------------

    duplicate_product_ids = df.loc[
        df["product_id"].duplicated(keep=False),
        "product_id",
    ].tolist()

    duplicate_id_web = df.loc[
        df["id_web"].duplicated(keep=False),
        "id_web",
    ].tolist()

    before_duplicates = len(df)

    # Une ligne de liaison doit être unique
    df = df.drop_duplicates(
        subset=[
            "product_id",
            "id_web",
        ],
        keep="first",
    ).copy()

    removed_duplicates = before_duplicates - len(df)

    # ---------------------------------------------------------
    # 3. Contrôle d'unicité de product_id
    # ---------------------------------------------------------

    product_id_multiple = df[
        df["product_id"].duplicated(keep=False)
    ]

    # ---------------------------------------------------------
    # 4. Contrôle d'unicité de id_web
    # ---------------------------------------------------------

    id_web_multiple = df[
        df["id_web"].duplicated(keep=False)
    ]

    # ---------------------------------------------------------
    # 5. Affichage des contrôles qualité
    # ---------------------------------------------------------

    print("=== Contrôle qualité table de liaison ===")

    print(
        f"Lignes initiales : {before_missing}"
    )

    print(
        f"Lignes après suppression des valeurs manquantes : "
        f"{len(df)}"
    )

    print(
        f"Lignes supprimées pour valeurs manquantes : "
        f"{removed_missing}"
    )

    print(
        f"Lignes supprimées pour doublons exacts : "
        f"{removed_duplicates}"
    )

    if duplicate_product_ids:
        print(
            "product_id apparaissant plusieurs fois : "
            f"{sorted(set(duplicate_product_ids))}"
        )
    else:
        print(
            "product_id multiples : aucun"
        )

    if duplicate_id_web:
        print(
            "id_web apparaissant plusieurs fois : "
            f"{sorted(set(duplicate_id_web))}"
        )
    else:
        print(
            "id_web multiples : aucun"
        )

    # ---------------------------------------------------------
    # 6. Contrôle des clés après nettoyage
    # ---------------------------------------------------------

    if not product_id_multiple.empty:
        print(
            "ATTENTION : certains product_id possèdent "
            "plusieurs correspondances."
        )
        print(
            product_id_multiple.to_string(index=False)
        )

    if not id_web_multiple.empty:
        print(
            "ATTENTION : certains id_web possèdent "
            "plusieurs correspondances."
        )
        print(
            id_web_multiple.to_string(index=False)
        )

    # ---------------------------------------------------------
    # 7. Vérification finale des valeurs
    # ---------------------------------------------------------

    if df["product_id"].isna().any():
        raise ValueError(
            "Des product_id sont encore manquants après nettoyage."
        )

    if df["id_web"].isna().any():
        raise ValueError(
            "Des id_web sont encore manquants après nettoyage."
        )

    return df


def save_liaison(df: pd.DataFrame) -> None:
    """Enregistrer la table de liaison préparée."""

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
        f"Nombre de correspondances : {len(df)}"
    )


def main() -> None:
    """Exécuter l'extraction de la table de liaison."""

    df = extract_liaison()
    save_liaison(df)


if __name__ == "__main__":
    main()
