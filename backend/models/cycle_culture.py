"""Modèle Cycle de Culture — instance d'une culture en cours ou terminée."""
from extensions import db


class CycleCulture(db.Model):
    __tablename__ = "cycle_culture"

    id_cycle = db.Column(db.Integer, primary_key=True)
    id_variete = db.Column(db.Integer, db.ForeignKey("variete_plante.id_variete"))
    id_recette = db.Column(db.Integer, db.ForeignKey("recette_culture.id_recette"))
    id_utilisateur = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"))
    date_debut = db.Column(db.Date, nullable=False)
    date_fin_prevue = db.Column(db.Date)
    date_fin_reelle = db.Column(db.Date)
    statut = db.Column(db.String(20), default="en_cours")  # en_cours, termine, abandonne
    notes = db.Column(db.Text)
    date_recolte_predite = db.Column(db.Date)  # Bonus

    # Relations
    lectures = db.relationship("LectureCapteur", backref="cycle", lazy="dynamic")
    commandes = db.relationship("CommandeActionneur", backref="cycle", lazy="dynamic")
    alertes = db.relationship("Alerte", backref="cycle", lazy="dynamic")
    suivis = db.relationship("SuiviCroissance", backref="cycle", lazy="dynamic")
    rapports = db.relationship("Rapport", backref="cycle", lazy="dynamic")

    def to_dict(self):
        return {
            "id_cycle": self.id_cycle,
            "id_variete": self.id_variete,
            "id_recette": self.id_recette,
            "id_utilisateur": self.id_utilisateur,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin_prevue": self.date_fin_prevue.isoformat() if self.date_fin_prevue else None,
            "date_fin_reelle": self.date_fin_reelle.isoformat() if self.date_fin_reelle else None,
            "statut": self.statut,
            "notes": self.notes,
            "date_recolte_predite": self.date_recolte_predite.isoformat() if self.date_recolte_predite else None,
            "variete_nom": self.variete.nom if self.variete else None,
            "recette_nom": self.recette.nom_recette if self.recette else None,
        }

    def __repr__(self):
        return f"<CycleCulture {self.id_cycle} ({self.statut})>"
