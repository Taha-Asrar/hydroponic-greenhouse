"""Routes — Commandes actionneurs (manuelles + historique)."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, socketio
from models.commande_actionneur import CommandeActionneur
from models.actionneur import Actionneur

commandes_bp = Blueprint("commandes", __name__)


@commandes_bp.route("", methods=["POST"])
@jwt_required()
def create_commande():
    """Envoyer une commande manuelle à un actionneur."""
    data = request.get_json()
    user_id = get_jwt_identity()

    required = ["id_actionneur", "etat"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400

    if data["etat"] not in ("ON", "OFF"):
        return jsonify({"error": "L'état doit être 'ON' ou 'OFF'"}), 400

    actionneur = Actionneur.query.get_or_404(data["id_actionneur"])

    # Si on active la pompe alimentation, activer aussi la pompe évacuation
    commandes = []
    commande = CommandeActionneur(
        id_actionneur=data["id_actionneur"],
        id_cycle=data.get("id_cycle"),
        id_utilisateur=int(user_id),
        etat=data["etat"],
        duree_secondes=data.get("duree_secondes"),
        source="manuel",
    )
    db.session.add(commande)
    commandes.append(commande)

    # Coordination des pompes : les deux fonctionnent en paire
    if actionneur.type in ("pompe_alimentation", "pompe_evacuation"):
        autre_type = "pompe_evacuation" if actionneur.type == "pompe_alimentation" else "pompe_alimentation"
        autre = Actionneur.query.filter_by(type=autre_type, actif=True).first()
        if autre:
            commande_paire = CommandeActionneur(
                id_actionneur=autre.id_actionneur,
                id_cycle=data.get("id_cycle"),
                id_utilisateur=int(user_id),
                etat=data["etat"],
                duree_secondes=data.get("duree_secondes"),
                source="manuel",
            )
            db.session.add(commande_paire)
            commandes.append(commande_paire)

    db.session.commit()

    result = [c.to_dict() for c in commandes]
    socketio.emit("nouvelles_commandes", result)
    return jsonify(result), 201


@commandes_bp.route("", methods=["GET"])
@jwt_required()
def get_commandes():
    """Historique des commandes. Filtres : id_cycle, id_actionneur, limit."""
    id_cycle = request.args.get("id_cycle", type=int)
    id_actionneur = request.args.get("id_actionneur", type=int)
    limit = request.args.get("limit", 50, type=int)

    query = CommandeActionneur.query
    if id_cycle:
        query = query.filter_by(id_cycle=id_cycle)
    if id_actionneur:
        query = query.filter_by(id_actionneur=id_actionneur)

    commandes = query.order_by(CommandeActionneur.horodatage.desc()).limit(limit).all()
    return jsonify([c.to_dict() for c in commandes]), 200
