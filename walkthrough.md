# Walkthrough : Sprint 2 - Logique Métier & Dashboard Temps Réel

Le développement du Sprint 2 vient d'être achevé avec succès. Voici les composants majeurs mis en place pour rendre la serre intelligente et réactive :

## 1. Moteur de Décision (Ebb & Flow)
- Création du `decision_engine.py` responsable de l'évaluation du cycle de culture.
- La logique métier implémentée simule une table à marée (Ebb & Flow). Le moteur surveille le capteur de niveau d'eau. 
- Lorsque l'eau est basse (<= 10 cm), la **Pompe d'alimentation** s'active.
- Lorsque l'eau est haute (>= 40 cm), la **Pompe d'évacuation** s'active.
- Ajout de `Flask-APScheduler` dans les dépendances pour exécuter cette logique de manière asynchrone toutes les 10 secondes en arrière-plan de notre application Flask.

## 2. Service Série (Mock/Arduino)
- Développement de `serial_service.py` pour orchestrer la communication avec la carte Arduino.
- Le système tente de se connecter sur le port par défaut (`COM3`). S'il ne détecte pas la carte Arduino, il bascule automatiquement en **Mode Simulation (Mock Mode)**. Cela permet de continuer à tester et développer l'interface web sans être bloqué par le matériel physique.

## 3. Communication en Temps Réel avec Socket.IO
- À chaque fois que le moteur de décision modifie l'état d'un actionneur, un événement WebSocket (`actuators_update`) est émis.
- Le frontend React (via `socket.io-client` dans `DashboardPage.jsx`) écoute cet événement et met à jour instantanément les cartes d'actionneurs sur l'interface, **sans que l'utilisateur n'ait besoin de rafraîchir la page**.

## 4. Restauration & Stabilité (Finalisation)
- Le projet a été entièrement restauré après une corruption de fichiers :
    - `App.jsx` a été reconstruit avec le système de navigation et les routes protégées.
    - `package.json` a été rétabli, assurant le bon fonctionnement de `npm run dev`.
    - La base de données a été ré-initialisée et peuplée via `seeds/seed_data.py`.
- L'interface est désormais 100% synchronisée avec le backend via WebSocket, affichant les changements d'état des pompes en direct.

## Guide pour la Suite (Équipe & IA)
Pour les autres membres du groupe ou pour continuer avec une IA :
1. **Contexte** : Toujours se référer au `README.md` racine pour l'architecture.
2. **Suivi** : Utiliser `task.md` pour savoir ce qui reste à faire (Sprint 3).
3. **Moteur** : Le cerveau est dans `backend/services/decision_engine.py`. Toute modification de la logique de culture doit se faire ici.
4. **Hardware** : Le passage de la simulation au réel se fait en changeant `SERIAL_PORT` dans le `.env`.

Les serveurs Backend (5000) et Frontend (5175) sont opérationnels.
Accès Admin : `admin@hydro.local` / `password123`.
