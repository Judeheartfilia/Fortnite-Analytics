# 🎮 Fortnite Creative Analytics Dashboard

Dashboard d'analyse des performances des jeux Fortnite Creative/UEFN à partir de données publiques (fortnite.gg).

## 🎯 Objectifs

- Identifier les jeux qui performent le mieux
- Comprendre quels concepts fonctionnent (tycoon, deathrun, PvP, etc.)
- Analyser les tendances et mécaniques de gameplay
- Évaluer la pertinence de Fortnite pour différents secteurs d'activité

## 📊 Métriques collectées

- Minutes Played (total + par joueur)
- Plays / Sessions
- Peak CCU (pic de joueurs simultanés)
- Unique Players
- Favorites
- Recommends
- Rétention (D1, D7)
- Date de sortie
- Évolution temporelle (7j, 30j)

## 🧩 Axes d'analyse

- **Genre** : Tycoon, Deathrun, Horror, PvP, Solo, etc.
- **Mécaniques** : Progression, Skill-based, Exploration, Combat, etc.
- **Secteur d'activité** : Banque, Food, Gaming, Médias, etc.

## 🚀 Installation
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le scraping
python scrapers/advanced_scraper.py
```

## 📂 Structure du projet
```
fortnite-analytics/
├── scrapers/          # Scripts de scraping
├── data/              # Données collectées
├── database/          # Base de données SQLite
├── dashboard/         # Dashboard HTML interactif
├── analysis/          # Scripts d'analyse
└── requirements.txt   # Dépendances
```

## 🎨 Dashboard

Le dashboard permet de :
- Filtrer par genre, mécanique, secteur
- Trier par n'importe quel KPI
- Comparer des groupes (solo vs PvP, etc.)
- Analyser l'évolution temporelle

## 📝 Notes

- Données publiques et estimées (objectif : tendances, pas précision absolue)
- Focus sur l'analyse comparative et stratégique
- Dashboard lisible et exploitable pour décisions produit/marketing