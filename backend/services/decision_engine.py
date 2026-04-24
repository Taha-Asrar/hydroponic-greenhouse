from models.capteur import Capteur
from models.actionneur import Actionneur
from extensions import db, socketio
import time

def get_latest_readings():
    """Retrieve the latest sensor readings (simulated or real)."""
    # In a real app, this would query LectureCapteur.
    # For now, we simulate based on active sensors.
    capteurs = Capteur.query.filter_by(actif=True).all()
    readings = {}
    for c in capteurs:
        # Provide a safe default reading
        readings[c.type_capteur] = 50.0  
    return readings

def evaluate_ebb_and_flow():
    """
    Logique Métier : Système Ebb & Flow (Table à Marée)
    1. Vérifie le niveau d'eau dans le bac de culture.
    2. Si le niveau est trop bas (début de cycle), active la pompe d'alimentation et coupe l'évacuation.
    3. Si le niveau atteint le maximum, coupe l'alimentation et active la pompe d'évacuation.
    """
    print("[Decision Engine] Évaluation du cycle Ebb & Flow...")
    
    # 1. Récupération de l'état des actionneurs
    pompe_in = Actionneur.query.filter_by(type="pompe_alimentation").first()
    pompe_out = Actionneur.query.filter_by(type="pompe_evacuation").first()
    
    if not pompe_in or not pompe_out:
        print("[Decision Engine] ERREUR: Pompes non configurées dans la base de données.")
        return

    # 2. Récupération des lectures de capteurs
    readings = get_latest_readings()
    niveau_eau = readings.get("niveau_eau", 0)  # Exemple: cm
    
    # 3. Logique de contrôle
    # Ces seuils devraient idéalement venir de la configuration du CycleCulture actif
    SEUIL_BAS = 10.0  # cm
    SEUIL_HAUT = 40.0 # cm
    
    changements = False

    # Logique : Si l'eau est basse, on remplit.
    if niveau_eau <= SEUIL_BAS:
        if not pompe_in.actif:
            pompe_in.actif = True
            print("[Decision Engine] Activation de la Pompe d'Alimentation (Niveau Bas)")
            changements = True
        if pompe_out.actif:
            pompe_out.actif = False
            print("[Decision Engine] Arret de la Pompe d'Evacuation")
            changements = True
            
    # Logique : Si l'eau est haute, on vide.
    elif niveau_eau >= SEUIL_HAUT:
        if pompe_in.actif:
            pompe_in.actif = False
            print("[Decision Engine] Arret de la Pompe d'Alimentation (Niveau Haut atteint)")
            changements = True
        if not pompe_out.actif:
            pompe_out.actif = True
            print("[Decision Engine] Activation de la Pompe d'Evacuation")
            changements = True

    # 4. Sauvegarde en DB si l'état des actionneurs a changé
    if changements:
        try:
            db.session.commit()
            print("[Decision Engine] Nouveaux états des actionneurs enregistrés.")
            
            # Émettre un événement Socket.IO pour informer le frontend
            socketio.emit('actuators_update', {
                'pompe_alimentation': pompe_in.actif,
                'pompe_evacuation': pompe_out.actif
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"[Decision Engine] Erreur lors de la sauvegarde: {e}")
    else:
        print("[Decision Engine] Aucun changement nécessaire.")

def run_decision_engine(app):
    """Point d'entrée pour le thread/scheduler d'évaluation en arrière-plan."""
    with app.app_context():
        # In a real scenario, this would loop or be called by a scheduler (like APScheduler)
        evaluate_ebb_and_flow()
