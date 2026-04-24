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

    # Example Format: SENSORS|niveau_eau:25.4|temp_eau:22.1|ec:1200
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
                    # Save history
                    lecture = LectureCapteur(id_capteur=capteur.id_capteur, valeur=value)
                    db.session.add(lecture)
                    # Update current
                    capteur.dernier_releve = value
            
            db.session.commit()
            
            # Broadcast to frontend
            socketio.emit('nouvelles_lectures', readings)
            print(f"[Sensors] Donnees lues et enregistrees: {readings}")

            # --- Vérification des seuils (Alertes) ---
            active_cycle = CycleCulture.query.filter_by(statut='en_cours').first()
            if active_cycle:
                recette = RecetteCulture.query.get(active_cycle.id_recette)
                if recette:
                    check_thresholds(active_cycle.id_cycle, readings, recette)
                    
        except Exception as e:
            db.session.rollback()
            print(f"[Sensors] Erreur de parsing des capteurs: {e}")

def update_actionneur_state(type_act, state, command):
    """Met à jour l'état d'un actionneur en DB et envoie la commande série."""
    act = Actionneur.query.filter_by(type=type_act).first()
    
    if act and not act.mode_automatique:
        # En mode manuel, on ne change rien automatiquement
        return False
        
    changed = False
    if act:
        if act.actif != state:
            act.actif = state
            changed = True
    
    serial_service.send_command(command)
    return changed

def check_thresholds(cycle_id, readings, recette):
    """Vérifie les seuils et régule les 4 actionneurs disponibles (LED, FAN, 2 PUMPS)."""
    alerts = []
    updates = {}
    
    # 1. EC (Conductivité / Nutriments) - Alerte uniquement (pas d'actionneur dédié)
    ec = readings.get("ec")
    if ec is not None:
        if recette.ec_min is not None and ec < recette.ec_min:
            alerts.append(f"ALERTE: EC trop bas ({ec} µS/cm). Ajoutez des nutriments manuellement.")
        elif recette.ec_max is not None and ec > recette.ec_max:
            alerts.append(f"ALERTE: EC trop haut ({ec} µS/cm). Diluez l'eau.")

    # 2. Température Eau - Alerte uniquement (pas de chauffage/refroidisseur)
    temp = readings.get("temp_eau")
    if temp is not None:
        if recette.temp_eau_min is not None and temp < recette.temp_eau_min:
            alerts.append(f"ALERTE: Eau trop froide ({temp}°C).")
        elif recette.temp_eau_max is not None and temp > recette.temp_eau_max:
            alerts.append(f"ALERTE: Eau trop chaude ({temp}°C).")

    # 3. Température Air / Humidité (Ventilateur)
    temp_air = readings.get("temp_air")
    humidite = readings.get("humidite_air")
    fan_needed = False
    
    if temp_air is not None and recette.temp_air_max is not None and temp_air > recette.temp_air_max:
        alerts.append(f"Temp. air haute ({temp_air}°C) -> Activation Ventilateur")
        fan_needed = True
    elif humidite is not None and recette.humidite_max is not None and humidite > recette.humidite_max:
        alerts.append(f"Humidité haute ({humidite}%) -> Activation Ventilateur")
        fan_needed = True
        
    if update_actionneur_state("ventilateur", fan_needed, f"FAN:{1 if fan_needed else 0}"):
        updates["ventilateur"] = fan_needed

    # 4. Luminosité (LED Grow)
    lux = readings.get("luminosite")
    if lux is not None:
        if recette.luminosite_min is not None and lux < recette.luminosite_min:
            if update_actionneur_state("eclairage", True, "LED:1"):
                updates["eclairage"] = True
        elif (recette.luminosite_max and lux > recette.luminosite_max) or lux > 50000:
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
    Logique Métier : Système Ebb & Flow (Table à Marée)
    """
    print("[Decision Engine] Évaluation du cycle Ebb & Flow...")
    
    pompe_in = Actionneur.query.filter_by(type="pompe_alimentation").first()
    pompe_out = Actionneur.query.filter_by(type="pompe_evacuation").first()
    
    if not pompe_in or not pompe_out:
        return

    # Si l'une des pompes est en mode manuel, on skip l'auto-regulation Ebb & Flow
    if not pompe_in.mode_automatique or not pompe_out.mode_automatique:
        print("[Decision Engine] Cycle Ebb & Flow en pause (Mode Manuel actif sur une pompe)")
        return

    readings = get_latest_readings()
    niveau_eau = readings.get("niveau_eau", 0)
    
    SEUIL_BAS = 10.0  # cm
    SEUIL_HAUT = 40.0 # cm
    
    changements = False

    if niveau_eau <= SEUIL_BAS:
        if not pompe_in.actif:
            pompe_in.actif = True
            serial_service.send_command("PUMP_IN:1")
            changements = True
        if pompe_out.actif:
            pompe_out.actif = False
            serial_service.send_command("PUMP_OUT:0")
            changements = True
            
    elif niveau_eau >= SEUIL_HAUT:
        if pompe_in.actif:
            pompe_in.actif = False
            serial_service.send_command("PUMP_IN:0")
            changements = True
        if not pompe_out.actif:
            pompe_out.actif = True
            serial_service.send_command("PUMP_OUT:1")
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
    """Point d'entrée pour le thread/scheduler d'évaluation en arrière-plan."""
    with app.app_context():
        # In a real scenario, this would loop or be called by a scheduler (like APScheduler)
        evaluate_ebb_and_flow()
