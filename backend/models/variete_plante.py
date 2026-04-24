"""Modèle Variété de Plante — espèces cultivables dans la serre."""
from extensions import db


class VarietePlante(db.Model):
    __tablename__ = "variete_plante"

    id_variete = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    duree_croissance_jours = db.Column(db.Integer, nullable=False)
    conditions_ideales = db.Column(db.Text)

    # Relations
    recettes = db.relationship("RecetteCulture", backref="variete", lazy="dynamic")
    cycles = db.relationship("CycleCulture", backref="variete", lazy="dynamic")

    def to_dict(self):
        return {
            "id_variete": self.id_variete,
            "nom": self.nom,
            "description": self.description,
            "duree_croissance_jours": self.duree_croissance_jours,
            "conditions_ideales": self.conditions_ideales,
        }

    def __repr__(self):
        return f"<VarietePlante {self.nom}>"
