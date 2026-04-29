from models.capteur import Capteur
from models.actionneur import Actionneur
from models.lecture_capteur import LectureCapteur
from models.cycle_culture import CycleCulture
from models.recette_culture import RecetteCulture
from extensions import db, socketio
from services.serial_service import serial_service
from services.notification_service import notification_service
import time

def process_sensor_data():
    """Read sensor data from Serial, save to DB and notify frontend."""
    data_str = serial_service.read_data()
    if not data_str:
        return

    if data_str.startswith("SENSORS|"):
        try:
            parts = data_str.split("|")[1:]
            readings = {}
            for p in parts:
                if ":" in p:
                    k, v = p.split(":")
                    readings[k] = float(v)
            
            # Save to DB
            for type_capteur, value in readings.items():
                capteur = Capteur.query.filter_by(type_capteur=type_capteur).first()
                if capteur:
                    lecture = LectureCapteur(id_capteur=capteur.id_capteur, valeur=value)
                    db.session.add(lecture)
                    capteur.dernier_releve = value
            
            db.session.commit()
            
            # Broadcast to frontend via WebSocket
            socketio.emit('nouvelles_lectures', readings)
            print(f"[Sensors] Donnees lues et enregistrees: {readings}")

            # --- Verification des seuils (Alertes) ---
            active_cycle = CycleCulture.query.filter_by(statut='en_cours').first()
            if active_cycle:
                recette = RecetteCulture.query.get(active_cycle.id_recette)
                if recette:
                    check_thresholds(active_cycle.id_cycle, readings, recette)
                    
        except Exception as e:
            db.session.rollback()
            print(f"[Sensors] Erreur de parsing des capteurs: {e}")

def update_actionneur_state(type_act, state, command):
    """Met a jour l'etat d'un actionneur en DB et envoie la commande serie."""
    act = Actionneur.query.filter_by(type=type_act).first()
    
    if act and not act.mode_automatique:
        return False
        
    changed = False
    if act:
        if act.actif != state:
            act.actif = state
            changed = True
    
    serial_service.send_command(command)
    return changed

def check_thresholds(cycle_id, readings, recette):
    """Verifie les seuils et regule les actionneurs (LED, FAN, 2 PUMPS)."""
    alerts = []
    updates = {}

    # 1. Temperature Eau -> Controle des Pompes
    temp_eau = readings.get("temp_eau")
    if temp_eau is not None and temp_eau > 0:
        if recette.temp_eau_max is not None and temp_eau > float(recette.temp_eau_max):
            alerts.append(f"Eau trop chaude ({temp_eau} C) -> Activation Pompes")
            if update_actionneur_state("pompe_alimentation", True, "PUMP_IN:1"):
                updates["pompe_alimentation"] = True
        elif recette.temp_eau_min is not None and temp_eau < float(recette.temp_eau_min):
            alerts.append(f"ALERTE: Eau trop froide ({temp_eau} C).")
            if update_actionneur_state("pompe_alimentation", False, "PUMP_IN:0"):
                updates["pompe_alimentation"] = False
        else:
            # Temperature eau dans la plage normale -> arreter les pompes
            if update_actionneur_state("pompe_alimentation", False, "PUMP_IN:0"):
                updates["pompe_alimentation"] = False

    # 2. Temperature Air / Humidite -> Ventilateur
    temp_air = readings.get("temp_air")
    humidite = readings.get("humidite")
    fan_needed = False
    
    if temp_air is not None and temp_air > 0:
        if recette.temp_air_max is not None and temp_air > float(recette.temp_air_max):
            alerts.append(f"Temp. air haute ({temp_air} C) -> Activation Ventilateur")
            fan_needed = True
    
    if not fan_needed and humidite is not None and humidite > 0:
        if recette.humidite_max is not None and humidite > float(recette.humidite_max):
            alerts.append(f"Humidite haute ({humidite}%) -> Activation Ventilateur")
            fan_needed = True
        
    if update_actionneur_state("ventilateur", fan_needed, f"FAN:{1 if fan_needed else 0}"):
        updates["ventilateur"] = fan_needed

    # 3. Luminosite -> LED Grow
    lux = readings.get("luminosite")
    if lux is not None:
        if recette.luminosite_min is not None and lux < float(recette.luminosite_min):
            if update_actionneur_state("eclairage", True, "LED:1"):
                updates["eclairage"] = True
        elif recette.luminosite_max is not None and lux > float(recette.luminosite_max):
             if update_actionneur_state("eclairage", False, "LED:0"):
                updates["eclairage"] = False

    # Sauvegarde
    if updates or alerts:
        try:
            for msg in alerts:
                notification_service.create_alert(cycle_id, msg, severite="warning")
            db.session.commit()
            if updates:
                socketio.emit('actuators_update', updates)
        except Exception as e:
            db.session.rollback()
            print(f"[Decision Engine] Erreur commit: {e}")

def get_latest_readings():
    """Retrieve the latest sensor readings from the DB."""
    capteurs = Capteur.query.filter_by(actif=True).all()
    readings = {}
    for c in capteurs:
        readings[c.type_capteur] = c.dernier_releve or 0.0  
    return readings

def evaluate_ebb_and_flow():
    """
    Logique Metier : Systeme Ebb & Flow (Table a Maree)
    Les pompes sont controlees par la temperature de l'eau.
    """
    print("[Decision Engine] Evaluation du cycle Ebb & Flow...")
    
    pompe_in = Actionneur.query.filter_by(type="pompe_alimentation").first()
    pompe_out = Actionneur.query.filter_by(type="pompe_evacuation").first()
    
    if not pompe_in or not pompe_out:
        return

    if not pompe_in.mode_automatique or not pompe_out.mode_automatique:
        print("[Decision Engine] Cycle Ebb & Flow en pause (Mode Manuel actif sur une pompe)")
        return

    readings = get_latest_readings()
    temp_eau = readings.get("temp_eau", 0)
    
    # Recuperer les seuils de la recette active
    active_cycle = CycleCulture.query.filter_by(statut='en_cours').first()
    if not active_cycle:
        return
    
    recette = RecetteCulture.query.get(active_cycle.id_recette)
    if not recette:
        return
    
    seuil_bas = float(recette.temp_eau_min) if recette.temp_eau_min else 16.0
    seuil_haut = float(recette.temp_eau_max) if recette.temp_eau_max else 26.0
    
    changements = False

    if temp_eau >= seuil_haut:
        # Eau trop chaude -> activer pompe pour circuler/refroidir
        if not pompe_in.actif:
            pompe_in.actif = True
            serial_service.send_command("PUMP_IN:1")
            changements = True
    elif temp_eau <= seuil_bas:
        # Eau trop froide -> arreter les pompes
        if pompe_in.actif:
            pompe_in.actif = False
            serial_service.send_command("PUMP_IN:0")
            changements = True

    if changements:
        try:
            db.session.commit()
            socketio.emit('actuators_update', {
                'pompe_alimentation': pompe_in.actif,
                'pompe_evacuation': pompe_out.actif
            })
        except Exception as e:
            db.session.rollback()
            print(f"[Decision Engine] Erreur commit Ebb & Flow: {e}")

def run_decision_engine(app):
    """Point d'entree pour le thread/scheduler d'evaluation en arriere-plan."""
    with app.app_context():
        evaluate_ebb_and_flow()
