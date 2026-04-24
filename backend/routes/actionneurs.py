"""Routes CRUD — Actionneurs."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models.actionneur import Actionneur
from extensions import db, socketio
from services.serial_service import serial_service

actionneurs_bp = Blueprint("actionneurs", __name__)


@actionneurs_bp.route("", methods=["GET"])
@jwt_required()
def get_actionneurs():
    """Liste tous les actionneurs enregistrés."""
    actionneurs = Actionneur.query.all()
    return jsonify([a.to_dict() for a in actionneurs]), 200


@actionneurs_bp.route("/status", methods=["GET"])
@jwt_required()
def get_hardware_status():
    """Vérifie si l'Arduino est réellement connecté."""
    return jsonify({
        "connected": serial_service.is_connected,
        "mock_mode": serial_service.mock_mode,
        "port": serial_service.serial_connection.port if serial_service.serial_connection else "None"
    }), 200


@actionneurs_bp.route("/<int:id_actionneur>/toggle", methods=["POST"])
@jwt_required()
def toggle_actionneur(id_actionneur):
    """Active ou désactive un actionneur manuellement et passe en mode MANUEL."""
    actionneur = Actionneur.query.get_or_404(id_actionneur)
    data = request.get_json()
    new_state = data.get("actif")
    
    if new_state is None:
        return jsonify({"msg": "Paramètre 'actif' manquant"}), 400
        
    actionneur.actif = new_state
    actionneur.mode_automatique = False # Désactiver l'automation pour cet actionneur
    db.session.commit()
    
    # Envoi de la commande à l'Arduino
    command_map = {
        "pompe_alimentation": "PUMP_IN",
        "pompe_evacuation": "PUMP_OUT",
        "eclairage": "LED",
        "ventilateur": "FAN"
    }
    
    cmd_prefix = command_map.get(actionneur.type)
    if cmd_prefix:
        cmd = f"{cmd_prefix}:{1 if new_state else 0}"
        serial_service.send_command(cmd)
    
    # Notification Socket.IO
    socketio.emit('actuators_update', {
        actionneur.type: new_state,
        f"{actionneur.type}_mode": "manuel"
    })
    
    return jsonify(actionneur.to_dict()), 200


@actionneurs_bp.route("/<int:id_actionneur>/auto", methods=["POST"])
@jwt_required()
def reset_auto(id_actionneur):
    """Repasse l'actionneur en mode AUTOMATIQUE."""
    actionneur = Actionneur.query.get_or_404(id_actionneur)
    actionneur.mode_automatique = True
    db.session.commit()
    
    socketio.emit('actuators_update', {
        f"{actionneur.type}_mode": "auto"
    })
    
    return jsonify(actionneur.to_dict()), 200


@actionneurs_bp.route("/<int:id_actionneur>", methods=["GET"])
@jwt_required()
def get_actionneur(id_actionneur):
    """Détail d'un actionneur."""
    actionneur = Actionneur.query.get_or_404(id_actionneur)
    return jsonify(actionneur.to_dict()), 200
