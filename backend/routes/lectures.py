"""Routes — Lectures de capteurs (enregistrement + historique)."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db, socketio
from models.lecture_capteur import LectureCapteur
from models.capteur import Capteur

lectures_bp = Blueprint("lectures", __name__)


@lectures_bp.route("", methods=["POST"])
@jwt_required()
def create_lecture():
    """
    Enregistrer une ou plusieurs lectures de capteurs.
    Accepte un objet unique ou un tableau.
    """
    data = request.get_json()

    # Normaliser en liste
    if isinstance(data, dict):
        data = [data]

    lectures = []
    for item in data:
        required = ["id_capteur", "valeur"]
        for field in required:
            if field not in item:
                return jsonify({"error": f"Le champ '{field}' est requis"}), 400

        lecture = LectureCapteur(
            id_capteur=item["id_capteur"],
            id_cycle=item.get("id_cycle"),
            valeur=item["valeur"],
            qualite=item.get("qualite", "ok"),
        )
        db.session.add(lecture)
        lectures.append(lecture)

    db.session.commit()

    # Émettre les lectures en temps réel via WebSocket
    result = [l.to_dict() for l in lectures]
    socketio.emit("nouvelles_lectures", result)

    return jsonify(result), 201


@lectures_bp.route("", methods=["GET"])
@jwt_required()
def get_lectures():
    """
    Historique des lectures. Filtres : id_cycle, id_capteur, limit.
    """
    id_cycle = request.args.get("id_cycle", type=int)
    id_capteur = request.args.get("id_capteur", type=int)
    limit = request.args.get("limit", 100, type=int)

    query = LectureCapteur.query

    if id_cycle:
        query = query.filter_by(id_cycle=id_cycle)
    if id_capteur:
        query = query.filter_by(id_capteur=id_capteur)

    lectures = query.order_by(LectureCapteur.horodatage.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in lectures]), 200


@lectures_bp.route("/derniere", methods=["GET"])
@jwt_required()
def get_dernieres_lectures():
    """Retourne la dernière lecture de chaque capteur actif."""
    capteurs = Capteur.query.filter_by(actif=True).all()
    result = []

    for capteur in capteurs:
        derniere = LectureCapteur.query.filter_by(
            id_capteur=capteur.id_capteur
        ).order_by(LectureCapteur.horodatage.desc()).first()

        entry = capteur.to_dict()
        if derniere:
            entry["derniere_lecture"] = derniere.to_dict()
        else:
            entry["derniere_lecture"] = None
        result.append(entry)

    return jsonify(result), 200
