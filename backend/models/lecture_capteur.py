"""Modèle Lecture Capteur — valeurs mesurées par les capteurs."""
from extensions import db
from datetime import datetime


class LectureCapteur(db.Model):
    __tablename__ = "lecture_capteur"

    id_lecture = db.Column(db.BigInteger, primary_key=True)
    id_capteur = db.Column(db.Integer, db.ForeignKey("capteur.id_capteur"))
    id_cycle = db.Column(db.Integer, db.ForeignKey("cycle_culture.id_cycle"))
    valeur = db.Column(db.Numeric, nullable=False)
    horodatage = db.Column(db.DateTime, default=datetime.utcnow)
    qualite = db.Column(db.String(10), default="ok")  # ok, suspect, erreur

    def to_dict(self):
        return {
            "id_lecture": self.id_lecture,
            "id_capteur": self.id_capteur,
            "id_cycle": self.id_cycle,
            "valeur": float(self.valeur),
            "horodatage": self.horodatage.isoformat() if self.horodatage else None,
            "qualite": self.qualite,
            "capteur_type": self.capteur.type_capteur if self.capteur else None,
            "capteur_unite": self.capteur.unite if self.capteur else None,
        }

    def __repr__(self):
        return f"<LectureCapteur {self.id_capteur}: {self.valeur}>"
