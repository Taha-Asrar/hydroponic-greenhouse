"""Modèle Capteur — capteurs physiques connectés à l'Arduino."""
from extensions import db


class Capteur(db.Model):
    __tablename__ = "capteur"

    id_capteur = db.Column(db.Integer, primary_key=True)
    type_capteur = db.Column(db.String(30))  # EC, temp_eau, temp_air, humidite, luminosite, niveau_eau
    nom = db.Column(db.String(150), nullable=False)
    unite = db.Column(db.String(20), nullable=False)
    valeur_min_possible = db.Column(db.Numeric)
    valeur_max_possible = db.Column(db.Numeric)
    actif = db.Column(db.Boolean, default=True)
    port_serie = db.Column(db.String(50))

    # Relations
    lectures = db.relationship("LectureCapteur", backref="capteur", lazy="dynamic")
    alertes = db.relationship("Alerte", backref="capteur", lazy="dynamic")

    def to_dict(self):
        return {
            "id_capteur": self.id_capteur,
            "type_capteur": self.type_capteur,
            "nom": self.nom,
            "unite": self.unite,
            "valeur_min_possible": float(self.valeur_min_possible) if self.valeur_min_possible else None,
            "valeur_max_possible": float(self.valeur_max_possible) if self.valeur_max_possible else None,
            "actif": self.actif,
            "port_serie": self.port_serie,
        }

    def __repr__(self):
        return f"<Capteur {self.nom} ({self.type_capteur})>"
