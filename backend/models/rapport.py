"""Modèle Rapport — rapports PDF générés automatiquement."""
from extensions import db
from datetime import datetime


class Rapport(db.Model):
    __tablename__ = "rapport"

    id_rapport = db.Column(db.Integer, primary_key=True)
    id_cycle = db.Column(db.Integer, db.ForeignKey("cycle_culture.id_cycle"))
    id_utilisateur = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"))
    type = db.Column(db.String(20))  # rendement, croissance, resume_cycle
    date_generation = db.Column(db.DateTime, default=datetime.utcnow)
    chemin_pdf = db.Column(db.String(500))
    rendement_g = db.Column(db.Numeric)
    consommation_eau_l = db.Column(db.Numeric)

    def to_dict(self):
        return {
            "id_rapport": self.id_rapport,
            "id_cycle": self.id_cycle,
            "id_utilisateur": self.id_utilisateur,
            "type": self.type,
            "date_generation": self.date_generation.isoformat() if self.date_generation else None,
            "chemin_pdf": self.chemin_pdf,
            "rendement_g": float(self.rendement_g) if self.rendement_g else None,
            "consommation_eau_l": float(self.consommation_eau_l) if self.consommation_eau_l else None,
        }

    def __repr__(self):
        return f"<Rapport {self.type} ({self.date_generation})>"
