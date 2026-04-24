"""Routes — Rapports PDF."""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.rapport import Rapport
from models.cycle_culture import CycleCulture
from models.variete_plante import VarietePlante
from models.recette_culture import RecetteCulture
from services.pdf_service import pdf_service

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

    # Récupérer les données pour le PDF
    cycle = CycleCulture.query.get_or_404(data["id_cycle"])
    variete = VarietePlante.query.get(cycle.id_variete)
    recette = RecetteCulture.query.get(cycle.id_recette)
    
    # Chemin relatif pour le stockage
    filename = f"rapport_cycle_{cycle.id_cycle}_{datetime.now().strftime('%Y%H%M')}.pdf"
    # S'assurer que le dossier static/reports existe
    upload_dir = os.path.join(current_app.root_path, 'static', 'reports')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)

    # Appeler pdf_service pour générer le PDF
    pdf_service.generate_cycle_report(cycle, variete, recette, [], filepath)

    rapport = Rapport(
        id_cycle=cycle.id_cycle,
        id_utilisateur=int(user_id),
        type=data.get("type", "resume_cycle"),
        chemin_pdf=f"static/reports/{filename}",
    )
    db.session.add(rapport)
    db.session.commit()
    return jsonify(rapport.to_dict()), 201
