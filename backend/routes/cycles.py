"""Routes CRUD — Cycles de culture."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, timedelta

from extensions import db
from models.cycle_culture import CycleCulture
from models.variete_plante import VarietePlante

cycles_bp = Blueprint("cycles", __name__)


@cycles_bp.route("", methods=["GET"])
@jwt_required()
def get_cycles():
    """Liste tous les cycles. Filtre optionnel par statut."""
    statut = request.args.get("statut")
    query = CycleCulture.query
    if statut:
        query = query.filter_by(statut=statut)
    cycles = query.order_by(CycleCulture.date_debut.desc()).all()
    return jsonify([c.to_dict() for c in cycles]), 200


@cycles_bp.route("/<int:id_cycle>", methods=["GET"])
@jwt_required()
def get_cycle(id_cycle):
    """Détail d'un cycle."""
    cycle = CycleCulture.query.get_or_404(id_cycle)
    return jsonify(cycle.to_dict()), 200


@cycles_bp.route("", methods=["POST"])
@jwt_required()
def create_cycle():
    """Démarrer un nouveau cycle de culture."""
    data = request.get_json()
    user_id = get_jwt_identity()

    required = ["id_variete", "id_recette"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400

    # Calculer la date de fin prévue
    variete = VarietePlante.query.get(data["id_variete"])
    date_debut = date.today()
    date_fin_prevue = None
    if variete:
        date_fin_prevue = date_debut + timedelta(days=variete.duree_croissance_jours)

    cycle = CycleCulture(
        id_variete=data["id_variete"],
        id_recette=data["id_recette"],
        id_utilisateur=int(user_id),
        date_debut=date_debut,
        date_fin_prevue=date_fin_prevue,
        statut="en_cours",
        notes=data.get("notes"),
    )
    db.session.add(cycle)
    db.session.commit()

    return jsonify(cycle.to_dict()), 201


@cycles_bp.route("/<int:id_cycle>/terminer", methods=["PATCH"])
@jwt_required()
def terminer_cycle(id_cycle):
    """Terminer un cycle de culture."""
    cycle = CycleCulture.query.get_or_404(id_cycle)

    if cycle.statut != "en_cours":
        return jsonify({"error": "Ce cycle n'est pas en cours"}), 400

    cycle.statut = "termine"
    cycle.date_fin_reelle = date.today()
    cycle.notes = request.get_json().get("notes", cycle.notes) if request.get_json() else cycle.notes

    db.session.commit()
    return jsonify(cycle.to_dict()), 200


@cycles_bp.route("/<int:id_cycle>/abandonner", methods=["PATCH"])
@jwt_required()
def abandonner_cycle(id_cycle):
    """Abandonner un cycle de culture."""
    cycle = CycleCulture.query.get_or_404(id_cycle)

    if cycle.statut != "en_cours":
        return jsonify({"error": "Ce cycle n'est pas en cours"}), 400

    cycle.statut = "abandonne"
    cycle.date_fin_reelle = date.today()

    db.session.commit()
    return jsonify(cycle.to_dict()), 200


@cycles_bp.route("/actif", methods=["GET"])
@jwt_required()
def get_cycle_actif():
    """Retourne le cycle en cours (le plus récent)."""
    cycle = CycleCulture.query.filter_by(statut="en_cours").order_by(
        CycleCulture.date_debut.desc()
    ).first()

    if not cycle:
        return jsonify({"message": "Aucun cycle en cours"}), 404

    return jsonify(cycle.to_dict()), 200
