"""Modèle Notification — envoi d'alertes par email ou SMS."""
from extensions import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = "notification"

    id_notification = db.Column(db.BigInteger, primary_key=True)
    id_alerte = db.Column(db.BigInteger, db.ForeignKey("alerte.id_alerte"))
    id_utilisateur = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"))
    canal = db.Column(db.String(10))  # email, sms
    statut = db.Column(db.String(15), default="en_attente")  # en_attente, envoyee, echec
    horodatage = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id_notification": self.id_notification,
            "id_alerte": self.id_alerte,
            "id_utilisateur": self.id_utilisateur,
            "canal": self.canal,
            "statut": self.statut,
            "horodatage": self.horodatage.isoformat() if self.horodatage else None,
        }

    def __repr__(self):
        return f"<Notification {self.canal} ({self.statut})>"
