"""Routes CRUD — Variétés de plantes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models.variete_plante import VarietePlante

varietes_bp = Blueprint("varietes", __name__)


@varietes_bp.route("", methods=["GET"])
@jwt_required()
def get_varietes():
    """Liste toutes les variétés de plantes."""
    varietes = VarietePlante.query.all()
    return jsonify([v.to_dict() for v in varietes]), 200


@varietes_bp.route("/<int:id_variete>", methods=["GET"])
@jwt_required()
def get_variete(id_variete):
    """Détail d'une variété."""
    variete = VarietePlante.query.get_or_404(id_variete)
    return jsonify(variete.to_dict()), 200


@varietes_bp.route("", methods=["POST"])
@jwt_required()
def create_variete():
    """Créer une nouvelle variété."""
    data = request.get_json()

    required = ["nom", "duree_croissance_jours"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400

    variete = VarietePlante(
        nom=data["nom"],
        description=data.get("description"),
        duree_croissance_jours=data["duree_croissance_jours"],
        conditions_ideales=data.get("conditions_ideales"),
    )
    db.session.add(variete)
    db.session.commit()

    return jsonify(variete.to_dict()), 201


@varietes_bp.route("/<int:id_variete>", methods=["PUT"])
@jwt_required()
def update_variete(id_variete):
    """Modifier une variété."""
    variete = VarietePlante.query.get_or_404(id_variete)
    data = request.get_json()

    variete.nom = data.get("nom", variete.nom)
    variete.description = data.get("description", variete.description)
    variete.duree_croissance_jours = data.get("duree_croissance_jours", variete.duree_croissance_jours)
    variete.conditions_ideales = data.get("conditions_ideales", variete.conditions_ideales)

    db.session.commit()
    return jsonify(variete.to_dict()), 200


@varietes_bp.route("/<int:id_variete>", methods=["DELETE"])
@jwt_required()
def delete_variete(id_variete):
    """Supprimer une variété."""
    variete = VarietePlante.query.get_or_404(id_variete)
    db.session.delete(variete)
    db.session.commit()
    return jsonify({"message": "Variété supprimée"}), 200
