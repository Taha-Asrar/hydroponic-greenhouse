"""
Modèles SQLAlchemy — Serre Hydroponique
Importe tous les modèles pour que Flask-Migrate les détecte.
"""
from models.utilisateur import Utilisateur
from models.variete_plante import VarietePlante
from models.recette_culture import RecetteCulture
from models.cycle_culture import CycleCulture
from models.capteur import Capteur
from models.lecture_capteur import LectureCapteur
from models.actionneur import Actionneur
from models.commande_actionneur import CommandeActionneur
from models.alerte import Alerte
from models.notification import Notification
from models.suivi_croissance import SuiviCroissance
from models.rapport import Rapport

__all__ = [
    "Utilisateur", "VarietePlante", "RecetteCulture",
    "CycleCulture", "Capteur", "LectureCapteur",
    "Actionneur", "CommandeActionneur", "Alerte",
    "Notification", "SuiviCroissance", "Rapport",
]
