"""Routes CRUD — Capteurs."""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from models.capteur import Capteur

capteurs_bp = Blueprint("capteurs", __name__)


@capteurs_bp.route("", methods=["GET"])
@jwt_required()
def get_capteurs():
    """Liste tous les capteurs."""
    capteurs = Capteur.query.filter_by(actif=True).all()
    return jsonify([c.to_dict() for c in capteurs]), 200


@capteurs_bp.route("/<int:id_capteur>", methods=["GET"])
@jwt_required()
def get_capteur(id_capteur):
    """Détail d'un capteur."""
    capteur = Capteur.query.get_or_404(id_capteur)
    return jsonify(capteur.to_dict()), 200
