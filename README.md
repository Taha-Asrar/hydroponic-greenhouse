# 🌱 Serre Hydroponique Urbaine Intelligente

Système automatisé de suivi et de contrôle d'une serre hydroponique urbaine. Le serveur (PC) est le cerveau du système : il prend toutes les décisions de dosage, d'irrigation et d'éclairage. L'Arduino se limite à la lecture des capteurs et à l'exécution des commandes.

## 📋 Table des matières

- [Architecture](#architecture)
- [Stack Technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [API REST](#api-rest)
- [Équipe](#équipe)

## 🏗️ Architecture

```
┌─────────────────┐     USB Série     ┌──────────────────────────────────┐
│   Arduino UNO   │◄────────────────►│        Serveur PC               │
│                 │                   │                                  │
│  • 6 Capteurs   │                   │  Flask API ──► PostgreSQL       │
│  • 2 Pompes     │                   │      │                          │
│  • 1 Éclairage  │                   │  SocketIO ──► React Dashboard  │
└─────────────────┘                   └──────────────────────────────────┘
```

**Système hydraulique (Ebb & Flow)** :
- **Pompe Alimentation** : verse l'eau + nutriments du réservoir vers le bac de culture
- **Pompe Évacuation** : draine l'eau usée du bac de culture
- Les deux pompes fonctionnent en coordination

## 🛠️ Stack Technique

| Couche | Technologie |
|--------|------------|
| Backend | Python 3.11+ / Flask |
| Base de données | PostgreSQL 16 |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | JWT (Flask-JWT-Extended) |
| Temps réel | Flask-SocketIO |
| Frontend | React.js 18 (Vite) |
| Communication | PySerial (USB) |
| Rapports | ReportLab (PDF) |

## 📦 Prérequis

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 16+
- **Arduino IDE** (pour la partie matérielle)

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd hydroponic-greenhouse
```

### 2. Base de données

```bash
# Créer la base de données
psql -U postgres -c "CREATE DATABASE serre_hydroponique;"

# Exécuter le schéma
psql -U postgres -d serre_hydroponique -f database/schema.sql
```

### 3. Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
copy .env.example .env
# → Éditer .env avec vos paramètres

# Lancer les migrations
flask db upgrade

# Lancer le serveur
python app.py
```

Le backend sera accessible sur `http://localhost:5000`

### 4. Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

## 📁 Structure du projet

```
hydroponic-greenhouse/
├── arduino/            # Code Arduino (.ino)
├── backend/            # API Flask + logique métier
│   ├── models/         # Modèles SQLAlchemy
│   ├── routes/         # Endpoints API REST
│   ├── services/       # Logique métier (série, décisions, alertes)
│   ├── app.py          # Point d'entrée
│   └── config.py       # Configuration
├── database/           # Scripts SQL
│   └── schema.sql      # Schéma de création + seed data
├── frontend/           # Application React (Vite)
│   └── src/
│       ├── components/ # Composants réutilisables
│       ├── pages/      # Pages de l'application
│       ├── api/        # Client HTTP (Axios)
│       └── context/    # Contexte React (Auth)
└── docs/               # Documentation et diagrammes
```

## 🔌 API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/register` | Inscription |
| POST | `/api/auth/login` | Connexion → JWT |
| GET/POST | `/api/varietes` | Variétés de plantes |
| GET/POST | `/api/recettes` | Recettes de culture |
| GET/POST | `/api/cycles` | Cycles de culture |
| GET | `/api/capteurs` | Capteurs |
| POST | `/api/lectures` | Enregistrer lectures |
| GET/POST | `/api/commandes` | Commandes actionneurs |
| GET | `/api/alertes` | Alertes |
| PATCH | `/api/alertes/:id/acquitter` | Acquitter alerte |
| POST | `/api/rapports/generer` | Générer rapport PDF |

## 🤖 Guide de Collaboration (Équipe & IA)

Ce projet est conçu pour être développé en collaboration avec des agents IA (comme Antigravity, Claude, etc.).

### Comment continuer le projet avec une IA ?
Pour que l'IA comprenne instantanément l'état du projet, donnez-lui accès aux fichiers suivants dès le début de la conversation :
1. **`README.md`** : Pour l'architecture globale.
2. **`task.md`** (dans le dossier de l'IA) : Pour connaître les tâches restantes.
3. **`walkthrough.md`** : Pour comprendre ce qui a été fait récemment.

**Instruction suggérée pour l'IA** :
> "Analyse le `README.md` racine et le `task.md` pour comprendre l'état actuel. Nous en sommes au **Sprint 3**. Ma prochaine tâche est de [Insérer tâche ici, ex: Implémenter les graphiques]."

### Recommandations pour l'équipe
- **Scripts de test** : Utilisez le dossier `backend/tests` pour valider vos changements.
- **Mode Simulation** : Si vous n'avez pas l'Arduino, l'API bascule automatiquement en "Mock". Vous pouvez forcer ce mode dans `backend/services/serial_service.py`.
- **Base de données** : Si vous modifiez les modèles, n'oubliez pas de lancer `flask db migrate` et `flask db upgrade`.

## 👥 Équipe

Projet réalisé dans le cadre du cours Arduino — ISCAE Casablanca.

## 📄 Licence

Projet académique — Usage éducatif uniquement.