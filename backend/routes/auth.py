"""
Routes d'authentification — inscription, connexion, profil.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import bcrypt

from extensions import db
from models.utilisateur import Utilisateur

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Inscription d'un nouvel utilisateur."""
    data = request.get_json()

    # Validation
    required = ["nom", "prenom", "email", "mot_de_passe"]
    for field in required:
        if field not in data or not data[field]:
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400

    # Vérifier si l'email existe déjà
    if Utilisateur.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Cet email est déjà utilisé"}), 409

    # Hash du mot de passe
    password_hash = bcrypt.hashpw(
        data["mot_de_passe"].encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    # Création de l'utilisateur
    utilisateur = Utilisateur(
        nom=data["nom"],
        prenom=data["prenom"],
        email=data["email"],
        mot_de_passe_hash=password_hash,
        role=data.get("role", "operateur"),
    )
    db.session.add(utilisateur)
    db.session.commit()

    return jsonify({
        "message": "Utilisateur créé avec succès",
        "utilisateur": utilisateur.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Connexion — retourne un token JWT."""
    data = request.get_json()

    if not data or not data.get("email") or not data.get("mot_de_passe"):
        return jsonify({"error": "Email et mot de passe requis"}), 400

    utilisateur = Utilisateur.query.filter_by(email=data["email"]).first()

    if not utilisateur or not utilisateur.actif:
        return jsonify({"error": "Identifiants invalides"}), 401

    # Vérification du mot de passe
    if not bcrypt.checkpw(
        data["mot_de_passe"].encode("utf-8"),
        utilisateur.mot_de_passe_hash.encode("utf-8"),
    ):
        return jsonify({"error": "Identifiants invalides"}), 401

    # Création du token JWT
    access_token = create_access_token(
        identity=str(utilisateur.id_utilisateur),
        additional_claims={
            "role": utilisateur.role,
            "nom": utilisateur.nom,
            "prenom": utilisateur.prenom,
        },
    )

    return jsonify({
        "access_token": access_token,
        "utilisateur": utilisateur.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """Retourne le profil de l'utilisateur connecté."""
    user_id = get_jwt_identity()
    utilisateur = Utilisateur.query.get(int(user_id))

    if not utilisateur:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    return jsonify(utilisateur.to_dict()), 200
