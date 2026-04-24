"""Routes CRUD — Suivi de croissance."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.suivi_croissance import SuiviCroissance

suivi_bp = Blueprint("suivi", __name__)


@suivi_bp.route("", methods=["GET"])
@jwt_required()
def get_suivis():
    """Liste les suivis. Filtre par id_cycle."""
    id_cycle = request.args.get("id_cycle", type=int)
    query = SuiviCroissance.query
    if id_cycle:
        query = query.filter_by(id_cycle=id_cycle)
    suivis = query.order_by(SuiviCroissance.date_mesure.desc()).all()
    return jsonify([s.to_dict() for s in suivis]), 200


@suivi_bp.route("", methods=["POST"])
@jwt_required()
def create_suivi():
    """Enregistrer une mesure de croissance."""
    data = request.get_json()
    user_id = get_jwt_identity()

    required = ["id_cycle", "date_mesure"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400

    suivi = SuiviCroissance(
        id_cycle=data["id_cycle"],
        id_utilisateur=int(user_id),
        date_mesure=data["date_mesure"],
        hauteur_cm=data.get("hauteur_cm"),
        poids_g=data.get("poids_g"),
        observations=data.get("observations"),
        photo_path=data.get("photo_path"),
    )
    db.session.add(suivi)
    db.session.commit()
    return jsonify(suivi.to_dict()), 201
