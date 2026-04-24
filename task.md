# 🌱 Serre Hydroponique — Task Tracker

## Sprint 1 — Fondations
- [x] .gitignore complet
- [x] README.md professionnel
- [x] database/schema.sql (copie du schéma)
- [x] backend/.env.example
- [x] requirements.txt complet
- [x] config.py (configuration Flask)
- [x] extensions.py (SQLAlchemy, Migrate, JWT, SocketIO)
- [x] app.py (point d'entrée Flask + blueprints)
- [x] Modèles SQLAlchemy (11 tables)
- [x] Routes auth (register, login, JWT)
- [x] Routes CRUD (variétés, recettes, capteurs, actionneurs)
- [x] Script seed data
- [x] Tests unitaires auth
- [x] Init React + Vite
- [x] Structure (pages, components, api, context)
- [x] Design system CSS
- [x] Auth (login, contexte JWT, routes protégées)
- [x] Layout (Sidebar + Header + routing)

## Sprint 2 — Logique Métier & Dashboard Temps Réel
- [x] **Frontend** : Implémenter le Dashboard (`/capteurs` en visualisation)
- [x] **Frontend** : Créer les composants React interactifs pour contrôler les pompes (`ActuatorControl`, `SensorCard`)
- [x] **Backend** : Coder la logique métier principale (`decision_engine.py` - Cycle d'Ebb & Flow)
- [x] **Backend** : Implémenter la communication série avec l'Arduino (`serial_service.py`)
- [x] **Full-stack** : Mettre en place Socket.IO pour envoyer les lectures de actionneurs au Dashboard en temps réel.
- [x] **Système** : Restauration complète du projet après perte de contexte (App.jsx, package.json, DB seeding)

## Sprint 3 — Visualisation Avancée & Gestion (À venir)
- [ ] **Frontend** : Intégrer les graphiques Recharts pour l'historique des capteurs (Température, Humidité, EC)
- [ ] **Frontend** : Développer la page de gestion des Recettes de culture
- [ ] **Backend** : Implémenter la génération de rapports PDF (ReportLab)
- [ ] **Matériel** : Liaison physique avec l'Arduino et calibration des capteurs réels
