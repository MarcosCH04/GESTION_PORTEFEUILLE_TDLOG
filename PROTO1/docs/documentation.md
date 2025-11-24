investment-backtester/
├── backend/
│   ├── app/
│   │   ├── api.py
│   │   ├── calc.py
│   │   ├── data_fetcher.py
│   │   ├── db.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   ├── scripts/
│   │   └── init_db.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AssetSelector.jsx
│   │   │   ├── Charts.jsx
│   │   │   ├── PeriodSelector.jsx
│   │   │   ├── PortfolioTable.jsx
│   │   │   └── StrategyForm.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
│
|
├── infra/
│   └── init-postgres.sql
│
├── .env.example
├── docker-compose.yml
| ── documentation.md  
└── README.md 


# Documentation du projet *investment-backtester*

Ce fichier décrit le rôle précis de chaque fichier et dossier dans l'arborescence du projet. Il sert de guide pour comprendre l'organisation globale du frontend, du backend et de l'infrastructure.

---

## 📁 Racine du projet

### **`docker-compose.yml`**

Orchestre l'ensemble du projet via Docker. Définit trois services :

* **frontend** (React)
* **backend** (FastAPI)
* **db** (PostgreSQL)

Il configure les ports, les variables d'environnement et les volumes persistants.

### **`.env.example`**

Liste modèle des variables d'environnement nécessaires (clé secrète, URL DB, credentials Postgres). À copier en `.env` avant utilisation.

### **`README.md`** *(optionnel, à compléter)*

Fichier de présentation du projet : installation, utilisation, objectifs.

---

## 📁 backend/

Le backend est une API construite avec **FastAPI**. C'est elle qui :

* télécharge et stocke les données d'actifs,
* calcule les métriques financières,
* exécute les backtests,
* assure l'interface entre frontend et base de données.

### **`backend/Dockerfile`**

Image Docker pour lancer le backend. Installe Python + dépendances, puis exécute FastAPI avec Uvicorn.

### **`backend/requirements.txt`**

Liste des dépendances Python : FastAPI, SQLAlchemy, Pandas, Numpy, YFinance, etc.

### 📁 `backend/app/`

Contient tout le code Python du backend.

#### **`main.py`**

Point d'entrée de l'application FastAPI. Déclare l'application et importe les routes.

#### **`api.py`**

Définit les routes de l'API :

* `/assets` : liste des actifs disponibles,
* `/download/{asset}` : téléchargement des données d'un actif,
* `/backtest` : exécution d'un backtest.

#### **`data_fetcher.py`** *(si présent)*

Télécharge les données de marché (via YFinance) et les stocke localement ou en base de données.

#### **`calc.py`** *(si présent)*

Contient les fonctions financières :

* CAGR,
* volatilité,
* max drawdown,
* calcul du portefeuille,
* exécution de la stratégie.

#### **`db.py`** *(si ajouté plus tard)*

Initialisation SQLAlchemy + gestion de session DB.

#### **`models.py`** *(si ajouté plus tard)*

Définitions ORM : User, Asset, TimeSeries, BacktestJob.

#### **`schemas.py`** *(si ajouté plus tard)*

Schemas Pydantic pour la validation des requêtes et réponses.

#### **`auth.py`** *(si ajouté plus tard)*

Gestion JWT, authentification utilisateur.

### 📁 `backend/scripts/`

Contient des scripts utilitaires.

#### **`init_db.py`** *(optionnel)*

Initialisation de la base : création des tables, insertion d'actifs par défaut.

---

## 📁 frontend/

Le frontend est une application **React + Vite**. C’est l’interface utilisateur pour :

* sélectionner des actifs,
* définir les périodes d’analyse,
* afficher les courbes et les résultats de backtests.

### **`frontend/Dockerfile`**

Image Docker pour le frontend : installe Node + dépendances, lance Vite.

### **`frontend/package.json`**

Définit les dépendances (React, Chart.js, Tailwind), scripts (build, dev), et configuration du projet.

### 📁 `frontend/src/`

Code principal du frontend.

#### **`main.jsx`**

Point d’entrée React, rend l’application dans le DOM.

#### **`App.jsx`**

Composant principal : gestion des états globaux et intégration des sous-composants.

#### 📁 `components/`

Contient les composants UI. Par exemple :

* **`AssetSelector.jsx`** : sélection des actifs + réglage des poids.
* **`PeriodSelector.jsx`** : sélection de la période du backtest.
* **`Charts.jsx`** : affichage du graphique de portefeuille.
* **`StrategyForm.jsx`** : choix de la stratégie (DCA ou buy-and-hold).
* **`PortfolioTable.jsx`** : affichage des métriques par actif.

---

## 📁 infra/ *(optionnel)*

Dossier pour fichiers d’infrastructure.

### **`init-postgres.sql`**

Script SQL pour initialiser la base PostgreSQL (tables, seed data). Peut être utilisé automatiquement par Docker.

---

## 📁 data/ *(créé automatiquement par le backend)*

Contient les fichiers CSV téléchargés via YFinance.

---

## 📁 volumes Docker

Lorsque le projet tourne avec Docker, les données persistantes de Postgres seront stockées dans un volume `pgdata/` créé automatiquement.

---

# Résumé rapide

| Élément            | Rôle                                                             |
| ------------------ | ---------------------------------------------------------------- |
| **Backend**        | Télécharge les données, calcule métriques & backtests, API REST. |
| **Frontend**       | UI React, formulaires, graphiques, envoie requêtes API.          |
| **Database**       | Stockage des séries temporelles, utilisateurs, jobs.             |
| **docker-compose** | Lance l’ensemble facilement.                                     |

---

Si tu souhaites, je peux :

* Ajouter ce fichier dans le ZIP téléchargeable,
* L’étendre avec schémas UML, schémas API, diagrammes d’architecture,
* Ajouter une section "workflow utilisateur" ou "diagramme de séquence".

Souhaites‑tu une version plus détaillée ?
