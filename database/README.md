# 🗄️ Base de Données PostgreSQL

Ce dossier contient les scripts de structure pour la base de données de la serre.

## 🚀 Initialisation

### 1. Création de la base
```bash
psql -U postgres -c "CREATE DATABASE serre_hydroponique;"
```

### 2. Importation du schéma
Le fichier `schema.sql` contient la structure complète des 11 tables ainsi que des données de base (Variétés de test, Capteurs, Actionneurs).
```bash
psql -U postgres -d serre_hydroponique -f schema.sql
```

## 📊 Modèle de données
Les tables principales sont :
- `utilisateur` : Gestion des accès.
- `cycle_culture` : Le coeur du système (lie une plante à une recette).
- `lecture_capteur` : Historique des mesures.
- `commande_actionneur` : Historique des ordres envoyés à l'Arduino.
- `alerte` : Journal des anomalies détectées.

## 🔄 Migrations
Le projet utilise **Flask-Migrate** (Alembic) pour gérer les évolutions du schéma sans perdre de données. Les fichiers de migration se trouvent dans `backend/migrations`.
