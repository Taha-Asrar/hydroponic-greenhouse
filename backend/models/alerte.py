"""Modèle Alerte — alertes déclenchées par les dérives de paramètres."""
from extensions import db
from datetime import datetime


class Alerte(db.Model):
    __tablename__ = "alerte"

    id_alerte = db.Column(db.BigInteger, primary_key=True)
    id_cycle = db.Column(db.Integer, db.ForeignKey("cycle_culture.id_cycle"))
    id_capteur = db.Column(db.Integer, db.ForeignKey("capteur.id_capteur"))
    type_alerte = db.Column(db.String(30))  # derive_ec, derive_temp, niveau_bas, panne
    message = db.Column(db.Text, nullable=False)
    valeur_mesuree = db.Column(db.Numeric)
    valeur_seuil = db.Column(db.Numeric)
    severite = db.Column(db.String(10), default="info")  # info, warning, critique
    horodatage = db.Column(db.DateTime, default=datetime.utcnow)
    acquittee = db.Column(db.Boolean, default=False)
    horodatage_acquittement = db.Column(db.DateTime)
    id_utilisateur_ack = db.Column(
        db.Integer, db.ForeignKey("utilisateur.id_utilisateur")
    )

    # Relations
    notifications = db.relationship("Notification", backref="alerte", lazy="dynamic")
    utilisateur_ack = db.relationship(
        "Utilisateur",
        foreign_keys=[id_utilisateur_ack],
        backref="alertes_acquittees",
    )

    def to_dict(self):
        return {
            "id_alerte": self.id_alerte,
            "id_cycle": self.id_cycle,
            "id_capteur": self.id_capteur,
            "type_alerte": self.type_alerte,
            "message": self.message,
            "valeur_mesuree": float(self.valeur_mesuree) if self.valeur_mesuree else None,
            "valeur_seuil": float(self.valeur_seuil) if self.valeur_seuil else None,
            "severite": self.severite,
            "horodatage": self.horodatage.isoformat() if self.horodatage else None,
            "acquittee": self.acquittee,
            "horodatage_acquittement": self.horodatage_acquittement.isoformat() if self.horodatage_acquittement else None,
            "capteur_type": self.capteur.type_capteur if self.capteur else None,
        }

    def __repr__(self):
        return f"<Alerte {self.type_alerte} ({self.severite})>"
