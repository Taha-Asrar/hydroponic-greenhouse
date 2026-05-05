"""Modèle Commande Actionneur — historique des commandes ON/OFF."""
from extensions import db
from datetime import datetime


class CommandeActionneur(db.Model):
    __tablename__ = "commande_actionneur"

    id_commande = db.Column(db.BigInteger, primary_key=True)
    id_actionneur = db.Column(db.Integer, db.ForeignKey("actionneur.id_actionneur"))
    id_cycle = db.Column(db.Integer, db.ForeignKey("cycle_culture.id_cycle"))
    id_utilisateur = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"))
    etat = db.Column(db.String(5))  # ON, OFF
    duree_secondes = db.Column(db.Integer)
    source = db.Column(db.String(15), default="automatique")  # automatique, manuel
    horodatage = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id_commande": self.id_commande,
            "id_actionneur": self.id_actionneur,
            "id_cycle": self.id_cycle,
            "id_utilisateur": self.id_utilisateur,
            "etat": self.etat,
            "duree_secondes": self.duree_secondes,
            "source": self.source,
            "horodatage": self.horodatage.isoformat() if self.horodatage else None,
            "actionneur_nom": self.actionneur.nom if self.actionneur else None,
            "actionneur_type": self.actionneur.type if self.actionneur else None,
        }

    def __repr__(self):
        return f"<CommandeActionneur {self.id_actionneur} → {self.etat}>"
