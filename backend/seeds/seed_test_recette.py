"""
Seed script: Cree une recette de test + un cycle actif pour tester
les donnees reelles envoyees par l'Arduino.

Seuils calibres pour les capteurs reels :
  - DHT11       -> temp_air ~20-30 C, humidite ~40-80%
  - DS18B20     -> temp_eau ~18-28 C
  - LDR         -> luminosite 0-100%
  - SEN18       -> niveau_eau 0-100%

Usage: python seeds/seed_test_recette.py
"""
import os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import (
    Utilisateur, VarietePlante, RecetteCulture,
    CycleCulture, Capteur, Actionneur
)


def seed():
    app = create_app()
    with app.app_context():

        # 1. Donnees de base
        admin = Utilisateur.query.filter_by(email="admin@hydro.local").first()
        if not admin:
            admin = Utilisateur(nom="Admin", prenom="Super",
                                email="admin@hydro.local", role="admin")
            admin.set_password("password123")
            db.session.add(admin)
            db.session.flush()

        # Capteurs (sans EC)
        capteurs_def = [
            {"type_capteur": "temp_eau",     "nom": "Temperature Eau",   "unite": "C"},
            {"type_capteur": "temp_air",     "nom": "Temperature Air",   "unite": "C"},
            {"type_capteur": "humidite",     "nom": "Humidite Air",      "unite": "%"},
            {"type_capteur": "luminosite",   "nom": "Luminosite",        "unite": "%"},
            {"type_capteur": "niveau_eau",   "nom": "Niveau Eau",        "unite": "%"},
        ]
        for cd in capteurs_def:
            if not Capteur.query.filter_by(type_capteur=cd["type_capteur"]).first():
                db.session.add(Capteur(**cd))

        # Desactiver EC s'il existe
        ec_capteur = Capteur.query.filter_by(type_capteur="EC").first()
        if ec_capteur:
            ec_capteur.actif = False

        # Actionneurs
        actionneurs_def = [
            {"type": "pompe_alimentation", "nom": "Pompe Alimentation"},
            {"type": "pompe_evacuation",   "nom": "Pompe Evacuation"},
            {"type": "eclairage",          "nom": "Lampe"},
            {"type": "ventilateur",        "nom": "Ventilateur"},
        ]
        for ad in actionneurs_def:
            if not Actionneur.query.filter_by(type=ad["type"]).first():
                db.session.add(Actionneur(**ad))

        db.session.flush()

        # 2. Variete
        variete = VarietePlante.query.filter_by(nom="Laitue Pommee").first()
        if not variete:
            variete = VarietePlante(
                nom="Laitue Pommee",
                description="Laitue classique ideale pour l'hydroponie.",
                duree_croissance_jours=35
            )
            db.session.add(variete)
            db.session.flush()

        # 3. Recette de test (seuils realistes)
        recette = RecetteCulture.query.filter_by(
            nom_recette="Test Reel - Laitue"
        ).first()

        if not recette:
            recette = RecetteCulture(
                id_variete=variete.id_variete,
                nom_recette="Test Reel - Laitue",
                phase="croissance",
                # Temperature eau (DS18B20) : Facile a declencher en touchant le capteur
                temp_eau_min=15.0,
                temp_eau_max=22.0, # S'il fait plus de 22C, les pompes s'allument
                # Temperature air (DHT11) : Souffler dessus pour depasser 25C
                temp_air_min=18.0,
                temp_air_max=25.0, # Si air > 25C -> Ventilateur ON
                # Humidite (DHT11) : Souffler dessus pour depasser 60%
                humidite_min=40.0,
                humidite_max=60.0, # Si humidite > 60% -> Ventilateur ON
                # Luminosite (LDR) : Couvrir avec la main pour descendre < 50%
                luminosite_min=50.0, # Si < 50% (sombre) -> Lampe ON
                luminosite_max=85.0, # Si > 85% (tres clair) -> Lampe OFF
                luminosite_heures_jour=16,
                # Niveau eau
                niveau_eau_min=10.0,
            )
            db.session.add(recette)
            db.session.flush()
            print(f"[OK] Recette creee : '{recette.nom_recette}' (ID={recette.id_recette})")
        else:
            print(f"[INFO] Recette existante : '{recette.nom_recette}' (ID={recette.id_recette})")

        # 4. Cycle de culture actif
        cycle_actif = CycleCulture.query.filter_by(statut="en_cours").first()
        if not cycle_actif:
            cycle_actif = CycleCulture(
                id_variete=variete.id_variete,
                id_recette=recette.id_recette,
                id_utilisateur=admin.id_utilisateur,
                date_debut=date.today(),
                date_fin_prevue=date.today() + timedelta(days=35),
                statut="en_cours",
                notes="Cycle de test avec capteurs reels Arduino"
            )
            db.session.add(cycle_actif)
            db.session.flush()
            print(f"[OK] Cycle actif cree : ID={cycle_actif.id_cycle} (fin prevue: {cycle_actif.date_fin_prevue})")
        else:
            print(f"[INFO] Cycle actif existant : ID={cycle_actif.id_cycle}")

        db.session.commit()

        # Resume
        print("\n" + "="*50)
        print("   DONNEES DE TEST PRETES")
        print("="*50)
        print(f"  Admin     : admin@hydro.local / password123")
        print(f"  Variete   : {variete.nom} (ID={variete.id_variete})")
        print(f"  Recette   : {recette.nom_recette} (ID={recette.id_recette})")
        print(f"  Cycle     : ID={cycle_actif.id_cycle} - statut={cycle_actif.statut}")
        print(f"  Debut     : {cycle_actif.date_debut}")
        print(f"  Fin prevue: {cycle_actif.date_fin_prevue}")
        print("="*50)
        print("\nLancez le backend (python app.py) et connectez l'Arduino !")
        print("Les donnees reelles s'afficheront sur le dashboard.\n")


if __name__ == "__main__":
    seed()
