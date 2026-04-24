"""Routes CRUD — Actionneurs."""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models.actionneur import Actionneur

actionneurs_bp = Blueprint("actionneurs", __name__)


@actionneurs_bp.route("", methods=["GET"])
@jwt_required()
def get_actionneurs():
    """Liste tous les actionneurs actifs."""
    actionneurs = Actionneur.query.filter_by(actif=True).all()
    return jsonify([a.to_dict() for a in actionneurs]), 200


@actionneurs_bp.route("/<int:id_actionneur>", methods=["GET"])
@jwt_required()
def get_actionneur(id_actionneur):
    """Détail d'un actionneur."""
    actionneur = Actionneur.query.get_or_404(id_actionneur)
    return jsonify(actionneur.to_dict()), 200
