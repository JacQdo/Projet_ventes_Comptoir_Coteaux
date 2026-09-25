# Projet Ventes Comptoir Coteaux

Pipeline Data Engineering de traitement et de reporting des ventes du Comptoir Coteaux.

Le projet permet de :

* extraire et nettoyer les données ERP ;
* extraire et nettoyer les données Web ;
* traiter la table de liaison ERP ↔ Web ;
* croiser les différentes sources ;
* calculer le chiffre d'affaires ;
* identifier les vins Premium selon leur niveau de prix ;
* générer automatiquement les livrables commerciaux ;
* exécuter les traitements dans Docker ;
* orchestrer le pipeline avec Kestra.

---

## 1. Architecture du projet

```text
Projet_ventes_Comptoir_Coteaux/
│
├── data/
│   ├── raw/
│   │   ├── Fichier_ERP.xlsx
│   │   ├── Fichier_web.xlsx
│   │   └── fichier_liaison.xlsx
│   │
│   ├── processed/
│   │   ├── erp_products.csv
│   │   ├── web_products.csv
│   │   ├── liaison_products.csv
│   │   └── sales_products.csv
│   │
│   └── output/
│       ├── rapport_ca.xlsx
│       ├── vins_premium.csv
│       └── vins_ordinaires.csv
│
├── docs/
│
├── kestra/
│   └── flows/
│       └── monthly_report.yml
│
├── sql/
│
├── src/
│   ├── extract/
│   │   ├── extract_erp.py
│   │   ├── extract_web.py
│   │   └── extract_liaison.py
│   │
│   ├── transform/
│   │   └── transform_sales.py
│   │
│   └── reporting/
│       └── generate_reports.py
│
├── tests/
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
├── README.md
└── README_long.md
```

---

# 2. Sources de données

Le pipeline utilise trois fichiers Excel.

### ERP

```text
data/raw/Fichier_ERP.xlsx
```

Principales colonnes :

```text
product_id
onsale_web
price
stock_quantity
stock_status
```

### Web

```text
data/raw/Fichier_web.xlsx
```

Principales colonnes :

```text
sku
total_sales
post_type
```

Seuls les produits dont :

```text
post_type = product
```

sont conservés.

### Table de liaison

```text
data/raw/fichier_liaison.xlsx
```

Colonnes :

```text
product_id
id_web
```

Cette table permet de faire correspondre les identifiants ERP aux identifiants Web.

---

# 3. Pipeline de données

Le traitement suit les étapes suivantes :

```text
                    SOURCES
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
        ERP           WEB        LIAISON
          │            │            │
          ▼            ▼            ▼
   extract_erp   extract_web   extract_liaison
          │            │            │
          └────────────┼────────────┘
                       ▼
               transform_sales
                       │
                       ▼
              sales_products.csv
                       │
                       ▼
             generate_reports
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Excel       Premium       Ordinaire
```

---

# 4. Extraction ERP

Script :

```text
src/extract/extract_erp.py
```

Le script :

* charge le fichier ERP ;
* vérifie les colonnes attendues ;
* supprime les lignes contenant des valeurs manquantes ;
* supprime les doublons `product_id` ;
* contrôle les prix négatifs ;
* contrôle les stocks négatifs ;
* génère :

```text
data/processed/erp_products.csv
```

Les anomalies de prix ou de stock sont signalées dans le contrôle qualité mais conservées dans les données.

---

# 5. Extraction Web

Script :

```text
src/extract/extract_web.py
```

Le script :

* charge les données Web ;
* conserve les lignes correspondant aux produits ;
* nettoie les identifiants SKU ;
* nettoie les ventes ;
* contrôle les doublons ;
* contrôle les ventes négatives ;
* génère :

```text
data/processed/web_products.csv
```

---

# 6. Extraction de la table de liaison

Script :

```text
src/extract/extract_liaison.py
```

Le script :

* charge la table de correspondance ;
* supprime les valeurs manquantes ;
* supprime les doublons exacts ;
* contrôle les correspondances multiples ;
* génère :

```text
data/processed/liaison_products.csv
```

---

# 7. Transformation

Script :

```text
src/transform/transform_sales.py
```

La transformation réalise deux jointures.

### Jointure 1

```text
ERP.product_id
        ↓
LIAISON.product_id
```

### Jointure 2

```text
LIAISON.id_web
        ↓
WEB.sku
```

Les produits présents dans les trois sources sont ensuite conservés.

---

# 8. Calcul du chiffre d'affaires

Le chiffre d'affaires est calculé avec :

```text
CA = price × total_sales
```

Le résultat est stocké dans :

```text
ca
```

dans :

```text
data/processed/sales_products.csv
```

---

# 9. Classification Premium

Le prix est standardisé avec un z-score.

```text
z-score = (prix - moyenne) / écart-type
```

Un produit est classé Premium lorsque :

```text
price_zscore > 2
```

La colonne :

```text
premium
```

contient alors :

```text
True
```

ou :

```text
False
```

---

# 10. Reporting

Script :

```text
src/reporting/generate_reports.py
```

Le script produit automatiquement trois livrables.

### Rapport de chiffre d'affaires

```text
data/output/rapport_ca.xlsx
```

Il contient notamment :

* les produits ;
* les ventes ;
* les prix ;
* le chiffre d'affaires ;
* le total du chiffre d'affaires.

### Vins Premium

```text
data/output/vins_premium.csv
```

### Vins ordinaires

```text
data/output/vins_ordinaires.csv
```

Les deux listes sont triées par prix décroissant.

---

# 11. Résultats de référence

Une exécution complète du pipeline a produit les résultats suivants :

```text
Produits ERP                 : 825
Correspondances liaison      : 731
Produits Web                 : 712
Produits fusionnés           : 712

Chiffre d'affaires total     : 70 318,60 €

Vins Premium                 : 30
Vins ordinaires              : 682
```

Livrables générés :

```text
rapport_ca.xlsx
vins_premium.csv
vins_ordinaires.csv
```

Ces valeurs constituent le résultat de référence pour tester l'orchestration Kestra.

---

# 12. Installation Python

Créer et activer l'environnement virtuel :

```powershell
python -m venv env
```

Activation PowerShell :

```powershell
.\env\Scripts\Activate.ps1
```

Installer les dépendances :

```powershell
pip install -r requirements.txt
```

---

# 13. Exécution locale

### ERP

```powershell
python src/extract/extract_erp.py
```

### Web

```powershell
python src/extract/extract_web.py
```

### Liaison

```powershell
python src/extract/extract_liaison.py
```

### Transformation

```powershell
python src/transform/transform_sales.py
```

### Reporting

```powershell
python src/reporting/generate_reports.py
```

---

# 14. Docker

Le projet peut être exécuté dans un conteneur Docker.

Construire l'image :

```powershell
docker build -t ventes-coteaux:latest .
```

Vérifier l'image :

```powershell
docker images | Select-String "ventes-coteaux"
```

---

# 15. Test Docker

Le projet Windows est monté dans `/app` du conteneur.

Exemple :

```powershell
docker run --rm `
  -v "C:/Users/Utilisateur/Documents/courses/Projet_ventes_Comptoir_Coteaux:/app" `
  ventes-coteaux:latest `
  python /app/src/extract/extract_erp.py
```

La même méthode peut être utilisée pour les autres scripts.

### Transformation

```powershell
docker run --rm `
  -v "C:/Users/Utilisateur/Documents/courses/Projet_ventes_Comptoir_Coteaux:/app" `
  ventes-coteaux:latest `
  python /app/src/transform/transform_sales.py
```

### Reporting

```powershell
docker run --rm `
  -v "C:/Users/Utilisateur/Documents/courses/Projet_ventes_Comptoir_Coteaux:/app" `
  ventes-coteaux:latest `
  python /app/src/reporting/generate_reports.py
```

---

# 16. Vérification des livrables

Après exécution :

```powershell
Get-ChildItem .\data\output\
```

Les fichiers attendus sont :

```text
rapport_ca.xlsx
vins_premium.csv
vins_ordinaires.csv
```

---

# 17. Kestra

Kestra est utilisé pour orchestrer le pipeline.

Architecture :

```text
Kestra
  │
  ├── extract_erp
  │
  ├── extract_web
  │
  ├── extract_liaison
  │
  ├── transform_sales
  │
  ├── generate_reports
  │
  └── verify_reports
```

La logique métier reste dans les scripts Python.

Kestra assure principalement :

* l'orchestration ;
* les dépendances entre tâches ;
* l'exécution Docker ;
* la planification ;
* le suivi des exécutions ;
* la supervision du pipeline.

---

# 18. Infrastructure Kestra

L'environnement local utilise :

```text
Kestra
PostgreSQL 17
Docker Task Runner
```

Vérifier les services :

```powershell
docker compose ps
```

Les services attendus sont :

```text
kestra
kestra-postgres
```

L'interface Kestra est disponible sur :

```text
http://localhost:8080
```

---

# 19. Flow Kestra

Le flow principal est :

```text
kestra/flows/monthly_report.yml
```

Il orchestre le reporting mensuel.

Ordre logique :

```text
extract_erp
      │
      ├──────────────┐
      ▼              ▼
extract_web    extract_liaison
      │              │
      └──────┬───────┘
             ▼
      transform_sales
             │
             ▼
      generate_reports
             │
             ▼
       verify_reports
```

Le déclenchement mensuel est configuré avec :

```text
15 de chaque mois à 09:00
Europe/Paris
```

---

# 20. Philosophie d'architecture

Le projet suit une séparation claire des responsabilités.

### Python

Responsable de :

* extraction ;
* nettoyage ;
* contrôle qualité ;
* transformation ;
* calcul des indicateurs ;
* génération des rapports.

### Docker

Responsable de :

* fournir un environnement reproductible ;
* isoler les dépendances ;
* standardiser l'exécution.

### Kestra

Responsable de :

* orchestrer les tâches ;
* gérer les dépendances ;
* planifier les exécutions ;
* superviser les workflows.

Cette séparation permet de modifier l'orchestrateur sans réécrire la logique métier.

---

# 21. Contrôles qualité

Le pipeline effectue plusieurs contrôles :

* présence des colonnes attendues ;
* valeurs manquantes ;
* doublons ;
* identifiants uniques ;
* correspondances ERP/Web ;
* prix négatifs ;
* stocks négatifs ;
* ventes négatives ;
* cohérence des jointures.

Les anomalies détectées sont affichées dans les logs.

Exemple :

```text
ATTENTION : prix négatifs conservés dans les données
ATTENTION : quantités de stock négatives conservées dans les données
```

---

# 22. Technologies

```text
Python 3.12
Pandas
OpenPyXL
Docker
Docker Compose
Kestra
PostgreSQL 17
PowerShell
Git
```

---

# 23. Commandes utiles

### Voir les conteneurs

```powershell
docker ps
```

### Voir tous les conteneurs

```powershell
docker ps -a
```

### Voir les images

```powershell
docker images
```

### Logs Kestra

```powershell
docker logs kestra --tail 50
```

### Statut Docker Compose

```powershell
docker compose ps
```

### Arrêter Kestra

```powershell
docker compose down
```

### Redémarrer Kestra

```powershell
docker compose up -d
```

### Vérifier les fichiers de sortie

```powershell
Get-ChildItem .\data\output\
```

---

# 24. Git

Vérifier l'état du projet :

```powershell
git status
```

Ajouter les modifications :

```powershell
git add .
```

Créer un commit :

```powershell
git commit -m "feat: add automated monthly sales reporting"
```

Envoyer sur le dépôt distant :

```powershell
git push
```

---

# 25. Résultat attendu

À terme, une exécution du workflow Kestra doit permettre de passer automatiquement de :

```text
3 fichiers Excel sources
```

à :

```text
data/output/
├── rapport_ca.xlsx
├── vins_premium.csv
└── vins_ordinaires.csv
```

sans intervention manuelle dans les différentes étapes du traitement.

---

## 26. Statut du projet

### Pipeline Python

**VALIDÉ**

### Docker

**VALIDÉ**

### Accès aux fichiers Windows depuis Docker

**VALIDÉ**

### Transformation des données

**VALIDÉ**

### Génération des rapports

**VALIDÉ**

### Kestra

**INSTALLÉ ET OPÉRATIONNEL**

### Orchestration Kestra

**À VALIDER PAR UNE PREMIÈRE EXÉCUTION DU FLOW**

---

## 27. Auteur

Projet Data Engineering — **Ventes Comptoir Coteaux**

Objectif : construire un pipeline de données reproductible permettant l'extraction, la transformation, le contrôle qualité, l'analyse et le reporting automatisé des ventes.
