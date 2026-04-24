"""Routes — Rapports PDF."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.rapport import Rapport

rapports_bp = Blueprint("rapports", __name__)


@rapports_bp.route("", methods=["GET"])
@jwt_required()
def get_rapports():
    """Liste les rapports. Filtre par id_cycle."""
    id_cycle = request.args.get("id_cycle", type=int)
    query = Rapport.query
    if id_cycle:
        query = query.filter_by(id_cycle=id_cycle)
    rapports = query.order_by(Rapport.date_generation.desc()).all()
    return jsonify([r.to_dict() for r in rapports]), 200


@rapports_bp.route("/generer", methods=["POST"])
@jwt_required()
def generer_rapport():
    """Générer un rapport PDF pour un cycle."""
    data = request.get_json()
    user_id = get_jwt_identity()

    if not data or "id_cycle" not in data:
        return jsonify({"error": "Le champ 'id_cycle' est requis"}), 400

    # TODO: Appeler pdf_service pour générer le PDF
    rapport = Rapport(
        id_cycle=data["id_cycle"],
        id_utilisateur=int(user_id),
        type=data.get("type", "resume_cycle"),
        chemin_pdf=f"reports/rapport_cycle_{data['id_cycle']}.pdf",
    )
    db.session.add(rapport)
    db.session.commit()
    return jsonify(rapport.to_dict()), 201
