"""Modèle Suivi de Croissance — mesures manuelles de l'évolution des plantes."""
from extensions import db


class SuiviCroissance(db.Model):
    __tablename__ = "suivi_croissance"

    id_suivi = db.Column(db.Integer, primary_key=True)
    id_cycle = db.Column(db.Integer, db.ForeignKey("cycle_culture.id_cycle"))
    id_utilisateur = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"))
    date_mesure = db.Column(db.Date, nullable=False)
    hauteur_cm = db.Column(db.Numeric)
    poids_g = db.Column(db.Numeric)
    observations = db.Column(db.Text)
    photo_path = db.Column(db.String(500))

    def to_dict(self):
        return {
            "id_suivi": self.id_suivi,
            "id_cycle": self.id_cycle,
            "id_utilisateur": self.id_utilisateur,
            "date_mesure": self.date_mesure.isoformat() if self.date_mesure else None,
            "hauteur_cm": float(self.hauteur_cm) if self.hauteur_cm else None,
            "poids_g": float(self.poids_g) if self.poids_g else None,
            "observations": self.observations,
            "photo_path": self.photo_path,
        }

    def __repr__(self):
        return f"<SuiviCroissance {self.date_mesure}>"
