



                         ┌──────────────────────────────┐
                         │        SOURCES RAW           │
                         └──────────────┬───────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             │                          │                          │
             ▼                          ▼                          ▼
   ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
   │ Fichier_erp.xlsx│       │ Fichier_web.xlsx│       │fichier_liaison  │
   │                 │       │                 │       │     .xlsx       │
   │ product_id      │       │ sku             │       │ product_id      │
   │ price           │       │ price           │       │ id_web          │
   │ stock_quantity   │       │ ...             │       │                 │
   └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
            │                         │                         │
            │                         │                         │
            ▼                         ▼                         ▼
   ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
   │ extract_erp.py  │       │ extract_web.py  │       │extract_liaison  │
   │                 │       │                 │       │     .py         │
   │ Contrôles       │       │ Contrôles       │       │ Contrôles       │
   │ qualité         │       │ qualité         │       │ correspondance  │
   └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
            │                         │                         │
            └──────────────┬──────────┴──────────┬──────────────┘
                           │                     │
                           ▼                     ▼
                 ┌────────────────────────────────────┐
                 │          DATA PROCESSED             │
                 │                                    │
                 │ erp_products.csv                   │
                 │ web_products.csv                   │
                 │ liaison_products.csv               │
                 └────────────────┬───────────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │   transform_sales.py    │
                     │                         │
                     │ • jointure ERP / Web    │
                     │ • rapprochement produit │
                     │ • nettoyage             │
                     │ • calcul du CA          │
                     │ • classification        │
                     └────────────┬────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ sales_products.csv  │
                       │                      │
                       │ 712 produits         │
                       │ CA = 70 318,60 €     │
                       └──────────┬───────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    generate_reports.py    │
                    │                           │
                    │ • indicateurs             │
                    │ • vins premium             │
                    │ • vins ordinaires          │
                    │ • contrôle des sorties     │
                    └─────────────┬─────────────┘
                                  │
                 ┌────────────────┼─────────────────┐
                 │                │                 │
                 ▼                ▼                 ▼
       ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
       │rapport_ca.xlsx │ │vins_premium.csv│ │vins_ordinaires│
       │                │ │                │ │     .csv       │
       └────────────────┘ └────────────────┘ └────────────────┘


                    ORCHESTRATION
        ┌─────────────────────────────────────────┐
        │                 KESTRA                  │
        │                                         │
        │  extract_erp                             │
        │       │                                 │
        │       ├──────► extract_web              │
        │       │                                 │
        │       └──────► extract_liaison          │
        │                    │                    │
        │                    └──────┐             │
        │                           ▼             │
        │                    transform_sales      │
        │                           │             │
        │                           ▼             │
        │                    generate_reports      │
        │                           │             │
        │                           ▼             │
        │                      verify_reports     │
        └─────────────────────────────────────────┘

             Kestra orchestre
             Python traite
             Docker reproduit
             Git versionne



             Version simplifiée 


             ┌─────────────┐
│     ERP     │
└──────┬──────┘
       │
┌──────▼──────┐
│     WEB     │
└──────┬──────┘
       │
┌──────▼──────────┐
│ TABLE DE        │
│ CORRESPONDANCE  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│    EXTRACTION   │
│     Python      │
└────────┬────────┘
         ▼
┌─────────────────┐
│   QUALITÉ &     │
│   TRANSFORMATION│
└────────┬────────┘
         ▼
┌─────────────────┐
│ DATASET VENTES  │
│   712 produits  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ KPI / REPORTING │
│ 70 318,60 € CA  │
└────────┬────────┘
         ▼
 ┌───────┼────────┐
 ▼       ▼        ▼
XLSX   PREMIUM  ORDINAIRE