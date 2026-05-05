"""
Routes package — Enregistre tous les blueprints.
"""
from routes.auth import auth_bp
from routes.varietes import varietes_bp
from routes.recettes import recettes_bp
from routes.cycles import cycles_bp
from routes.capteurs import capteurs_bp
from routes.lectures import lectures_bp
from routes.actionneurs import actionneurs_bp
from routes.commandes import commandes_bp
from routes.alertes import alertes_bp
from routes.suivi import suivi_bp
from routes.rapports import rapports_bp


def register_blueprints(app):
    """Enregistre tous les blueprints sur l'application Flask."""
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(varietes_bp, url_prefix="/api/varietes")
    app.register_blueprint(recettes_bp, url_prefix="/api/recettes")
    app.register_blueprint(cycles_bp, url_prefix="/api/cycles")
    app.register_blueprint(capteurs_bp, url_prefix="/api/capteurs")
    app.register_blueprint(lectures_bp, url_prefix="/api/lectures")
    app.register_blueprint(actionneurs_bp, url_prefix="/api/actionneurs")
    app.register_blueprint(commandes_bp, url_prefix="/api/commandes")
    app.register_blueprint(alertes_bp, url_prefix="/api/alertes")
    app.register_blueprint(suivi_bp, url_prefix="/api/suivi")
    app.register_blueprint(rapports_bp, url_prefix="/api/rapports")
