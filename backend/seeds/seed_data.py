import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import Utilisateur, Capteur, Actionneur, VarietePlante

def seed_database():
    app = create_app()
    with app.app_context():
        # 1. Add admin user
        if not Utilisateur.query.filter_by(email="admin@hydro.local").first():
            admin = Utilisateur(
                nom="Admin",
                prenom="Super",
                email="admin@hydro.local",
                role="admin"
            )
            admin.set_password("password123")
            db.session.add(admin)

        # 2. Add Capteurs (sans EC)
        capteurs = [
            {"type_capteur": "temp_eau",   "nom": "Temperature Eau",   "unite": "C"},
            {"type_capteur": "temp_air",   "nom": "Temperature Air",   "unite": "C"},
            {"type_capteur": "humidite",   "nom": "Humidite Air",      "unite": "%"},
            {"type_capteur": "luminosite", "nom": "Luminosite",        "unite": "%"},
            {"type_capteur": "niveau_eau", "nom": "Niveau Eau",        "unite": "%"},
        ]
        
        for capteur_data in capteurs:
            if not Capteur.query.filter_by(type_capteur=capteur_data["type_capteur"]).first():
                c = Capteur(**capteur_data)
                db.session.add(c)

        # Desactiver le capteur EC s'il existe
        ec_capteur = Capteur.query.filter_by(type_capteur="EC").first()
        if ec_capteur:
            ec_capteur.actif = False

        # 3. Add Actionneurs
        actionneurs = [
            {"type": "pompe_alimentation", "nom": "Pompe Alimentation"},
            {"type": "pompe_evacuation",   "nom": "Pompe Evacuation"},
            {"type": "eclairage",          "nom": "Lampe"},
            {"type": "ventilateur",        "nom": "Ventilateur"}
        ]

        for actionneur_data in actionneurs:
            if not Actionneur.query.filter_by(type=actionneur_data["type"]).first():
                a = Actionneur(**actionneur_data)
                db.session.add(a)

        # 4. Add Varietes
        varietes = [
            {"nom": "Laitue Pommee", "description": "Laitue classique ideale pour l'hydroponie.", "duree_croissance_jours": 35},
            {"nom": "Basilic Grand Vert", "description": "Herbe aromatique tres parfumee.", "duree_croissance_jours": 28},
            {"nom": "Tomate Cerise", "description": "Variete naine pour serre.", "duree_croissance_jours": 60}
        ]

        for var_data in varietes:
            if not VarietePlante.query.filter_by(nom=var_data["nom"]).first():
                v = VarietePlante(**var_data)
                db.session.add(v)

        db.session.commit()
        print("Seed data added successfully!")

if __name__ == "__main__":
    seed_database()
