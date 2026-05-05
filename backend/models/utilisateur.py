"""Modèle Utilisateur — admin ou opérateur de la serre."""
from extensions import db
from datetime import datetime
import bcrypt


class Utilisateur(db.Model):
    __tablename__ = "utilisateur"

    id_utilisateur = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="operateur")
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    cycles = db.relationship("CycleCulture", backref="utilisateur", lazy="dynamic")
    commandes = db.relationship(
        "CommandeActionneur", backref="utilisateur", lazy="dynamic"
    )
    suivis = db.relationship("SuiviCroissance", backref="utilisateur", lazy="dynamic")
    rapports = db.relationship("Rapport", backref="utilisateur", lazy="dynamic")
    notifications = db.relationship(
        "Notification", backref="utilisateur", lazy="dynamic"
    )

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.mot_de_passe_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.mot_de_passe_hash.encode("utf-8"))


    def to_dict(self):
        return {
            "id_utilisateur": self.id_utilisateur,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "role": self.role,
            "actif": self.actif,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
        }

    def __repr__(self):
        return f"<Utilisateur {self.prenom} {self.nom}>"
