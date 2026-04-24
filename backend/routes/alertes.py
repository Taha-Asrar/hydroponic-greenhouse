"""Routes — Alertes (liste, acquittement)."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from models.alerte import Alerte

alertes_bp = Blueprint("alertes", __name__)


@alertes_bp.route("", methods=["GET"])
@jwt_required()
def get_alertes():
    """Liste les alertes. Filtres : id_cycle, severite, acquittee."""
    id_cycle = request.args.get("id_cycle", type=int)
    severite = request.args.get("severite")
    acquittee = request.args.get("acquittee")
    limit = request.args.get("limit", 50, type=int)

    query = Alerte.query
    if id_cycle:
        query = query.filter_by(id_cycle=id_cycle)
    if severite:
        query = query.filter_by(severite=severite)
    if acquittee is not None:
        query = query.filter_by(acquittee=acquittee.lower() == "true")

    alertes = query.order_by(Alerte.horodatage.desc()).limit(limit).all()
    return jsonify([a.to_dict() for a in alertes]), 200


@alertes_bp.route("/<int:id_alerte>/acquitter", methods=["PATCH"])
@jwt_required()
def acquitter_alerte(id_alerte):
    """Acquitter une alerte."""
    alerte = Alerte.query.get_or_404(id_alerte)
    user_id = get_jwt_identity()

    alerte.acquittee = True
    alerte.horodatage_acquittement = datetime.utcnow()
    alerte.id_utilisateur_ack = int(user_id)

    db.session.commit()
    return jsonify(alerte.to_dict()), 200
