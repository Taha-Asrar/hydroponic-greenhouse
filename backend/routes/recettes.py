"""Routes CRUD — Recettes de culture."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models.recette_culture import RecetteCulture

recettes_bp = Blueprint("recettes", __name__)


@recettes_bp.route("", methods=["GET"])
@jwt_required()
def get_recettes():
    """Liste toutes les recettes. Filtre optionnel par variété."""
    id_variete = request.args.get("id_variete", type=int)
    query = RecetteCulture.query
    if id_variete:
        query = query.filter_by(id_variete=id_variete)
    recettes = query.all()
    return jsonify([r.to_dict() for r in recettes]), 200


@recettes_bp.route("/<int:id_recette>", methods=["GET"])
@jwt_required()
def get_recette(id_recette):
    """Détail d'une recette."""
    recette = RecetteCulture.query.get_or_404(id_recette)
    return jsonify(recette.to_dict()), 200


@recettes_bp.route("", methods=["POST"])
@jwt_required()
def create_recette():
    """Créer une nouvelle recette de culture."""
    data = request.get_json()

    required = ["nom_recette", "id_variete"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400

    recette = RecetteCulture(
        id_variete=data["id_variete"],
        nom_recette=data["nom_recette"],
        phase=data.get("phase"),
        ec_min=data.get("ec_min"),
        ec_max=data.get("ec_max"),
        temp_eau_min=data.get("temp_eau_min"),
        temp_eau_max=data.get("temp_eau_max"),
        temp_air_min=data.get("temp_air_min"),
        temp_air_max=data.get("temp_air_max"),
        humidite_min=data.get("humidite_min"),
        humidite_max=data.get("humidite_max"),
        luminosite_min=data.get("luminosite_min"),
        luminosite_max=data.get("luminosite_max"),
        luminosite_heures_jour=data.get("luminosite_heures_jour"),
        niveau_eau_min=data.get("niveau_eau_min"),
    )
    db.session.add(recette)
    db.session.commit()

    return jsonify(recette.to_dict()), 201


@recettes_bp.route("/<int:id_recette>", methods=["PUT"])
@jwt_required()
def update_recette(id_recette):
    """Modifier une recette."""
    recette = RecetteCulture.query.get_or_404(id_recette)
    data = request.get_json()

    fields = [
        "nom_recette", "phase", "ec_min", "ec_max",
        "temp_eau_min", "temp_eau_max", "temp_air_min", "temp_air_max",
        "humidite_min", "humidite_max", "luminosite_min", "luminosite_max",
        "luminosite_heures_jour", "niveau_eau_min",
    ]
    for field in fields:
        if field in data:
            setattr(recette, field, data[field])

    db.session.commit()
    return jsonify(recette.to_dict()), 200


@recettes_bp.route("/<int:id_recette>", methods=["DELETE"])
@jwt_required()
def delete_recette(id_recette):
    """Supprimer une recette."""
    recette = RecetteCulture.query.get_or_404(id_recette)
    db.session.delete(recette)
    db.session.commit()
    return jsonify({"message": "Recette supprimée"}), 200
