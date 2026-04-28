import os
import sys

# Set up path to import app and models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import Utilisateur, Capteur, Actionneur, VarietePlante

def seed_database():
    app = create_app()
    with app.app_context():
        # Clean existing test data if any
        
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

        # 2. Add Capteurs
        capteurs = [
            {"type_capteur": "EC", "nom": "Capteur EC", "unite": "µS/cm"},
            {"type_capteur": "temp_eau", "nom": "Température Eau", "unite": "°C"},
            {"type_capteur": "temp_air", "nom": "Température Air", "unite": "°C"},
            {"type_capteur": "humidite", "nom": "Humidité Air", "unite": "%"},
            {"type_capteur": "luminosite", "nom": "Luminosité", "unite": "lux"},
            {"type_capteur": "niveau_eau", "nom": "Niveau Eau", "unite": "cm"}
        ]
        
        for capteur_data in capteurs:
            if not Capteur.query.filter_by(type_capteur=capteur_data["type_capteur"]).first():
                c = Capteur(**capteur_data)
                db.session.add(c)

        # 3. Add Actionneurs
        actionneurs = [
            {"type": "pompe_alimentation", "nom": "Pompe Alimentation"},
            {"type": "pompe_evacuation", "nom": "Pompe Évacuation"},
            {"type": "eclairage", "nom": "Lampe"},
            {"type": "ventilateur", "nom": "Ventilateur"}
        ]

        for actionneur_data in actionneurs:
            if not Actionneur.query.filter_by(type=actionneur_data["type"]).first():
                a = Actionneur(**actionneur_data)
                db.session.add(a)

        # 4. Add Varietes
        varietes = [
            {"nom": "Laitue Pommée", "description": "Laitue classique idéale pour l'hydroponie.", "duree_croissance_jours": 35},
            {"nom": "Basilic Grand Vert", "description": "Herbe aromatique très parfumée.", "duree_croissance_jours": 28},
            {"nom": "Tomate Cerise", "description": "Variété naine pour serre.", "duree_croissance_jours": 60}
        ]

        for var_data in varietes:
            if not VarietePlante.query.filter_by(nom=var_data["nom"]).first():
                v = VarietePlante(**var_data)
                db.session.add(v)

        db.session.commit()
        print("Seed data added successfully!")

if __name__ == "__main__":
    seed_database()
