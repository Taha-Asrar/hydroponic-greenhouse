"""Modèle Actionneur — pompes et éclairage contrôlés par le serveur."""
from extensions import db


class Actionneur(db.Model):
    __tablename__ = "actionneur"

    id_actionneur = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30))  # pompe_alimentation, pompe_evacuation, eclairage
    nom = db.Column(db.String(150), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    port_serie = db.Column(db.String(50))

    # Relations
    commandes = db.relationship("CommandeActionneur", backref="actionneur", lazy="dynamic")

    def to_dict(self):
        return {
            "id_actionneur": self.id_actionneur,
            "type": self.type,
            "nom": self.nom,
            "actif": self.actif,
            "port_serie": self.port_serie,
        }

    def __repr__(self):
        return f"<Actionneur {self.nom} ({self.type})>"
