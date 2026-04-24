"""Modèle Recette de Culture — paramètres cibles par phase de croissance."""
from extensions import db


class RecetteCulture(db.Model):
    __tablename__ = "recette_culture"

    id_recette = db.Column(db.Integer, primary_key=True)
    id_variete = db.Column(db.Integer, db.ForeignKey("variete_plante.id_variete"))
    nom_recette = db.Column(db.String(150), nullable=False)
    phase = db.Column(db.String(20))  # germination, croissance, floraison, recolte

    # Seuils EC (conductivité)
    ec_min = db.Column(db.Numeric)
    ec_max = db.Column(db.Numeric)

    # Seuils température eau
    temp_eau_min = db.Column(db.Numeric)
    temp_eau_max = db.Column(db.Numeric)

    # Seuils température air
    temp_air_min = db.Column(db.Numeric)
    temp_air_max = db.Column(db.Numeric)

    # Seuils humidité
    humidite_min = db.Column(db.Numeric)
    humidite_max = db.Column(db.Numeric)

    # Seuils luminosité
    luminosite_min = db.Column(db.Numeric)
    luminosite_max = db.Column(db.Numeric)
    luminosite_heures_jour = db.Column(db.Integer)

    # Niveau d'eau minimum
    niveau_eau_min = db.Column(db.Numeric)

    # Relations
    cycles = db.relationship("CycleCulture", backref="recette", lazy="dynamic")

    def to_dict(self):
        return {
            "id_recette": self.id_recette,
            "id_variete": self.id_variete,
            "nom_recette": self.nom_recette,
            "phase": self.phase,
            "ec_min": float(self.ec_min) if self.ec_min else None,
            "ec_max": float(self.ec_max) if self.ec_max else None,
            "temp_eau_min": float(self.temp_eau_min) if self.temp_eau_min else None,
            "temp_eau_max": float(self.temp_eau_max) if self.temp_eau_max else None,
            "temp_air_min": float(self.temp_air_min) if self.temp_air_min else None,
            "temp_air_max": float(self.temp_air_max) if self.temp_air_max else None,
            "humidite_min": float(self.humidite_min) if self.humidite_min else None,
            "humidite_max": float(self.humidite_max) if self.humidite_max else None,
            "luminosite_min": float(self.luminosite_min) if self.luminosite_min else None,
            "luminosite_max": float(self.luminosite_max) if self.luminosite_max else None,
            "luminosite_heures_jour": self.luminosite_heures_jour,
            "niveau_eau_min": float(self.niveau_eau_min) if self.niveau_eau_min else None,
        }

    def __repr__(self):
        return f"<RecetteCulture {self.nom_recette} ({self.phase})>"
