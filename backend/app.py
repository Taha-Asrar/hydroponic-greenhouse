"""
Serre Hydroponique — Point d'entrée Flask
==========================================
Lance le serveur avec : python app.py
"""
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from config import get_config
from extensions import db, migrate, jwt, socketio, cors, scheduler


def create_app(config_class=None):
    """Factory pattern — crée et configure l'application Flask."""
    app = Flask(__name__)

    # Charger la configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    scheduler.init_app(app)

    # Importer les modèles (pour que Migrate les détecte)
    with app.app_context():
        from models import (  # noqa: F401
            Utilisateur, VarietePlante, RecetteCulture,
            CycleCulture, Capteur, LectureCapteur,
            Actionneur, CommandeActionneur, Alerte,
            Notification, SuiviCroissance, Rapport,
        )

    # Enregistrer les blueprints
    from routes import register_blueprints
    register_blueprints(app)

    # Route de santé
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "service": "Serre Hydroponique API",
            "version": "1.0.0",
        }), 200

    # Gestionnaire d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Ressource non trouvée"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Erreur interne du serveur"}), 500

    from services.decision_engine import evaluate_ebb_and_flow, process_sensor_data
    from services.serial_service import serial_service
    from services.notification_service import notification_service
    
    with app.app_context():
        # Initialiser la connexion série au démarrage
        serial_service.connect(app.config.get('SERIAL_PORT', 'COM3'), app.config.get('SERIAL_BAUDRATE', 9600))

    # Wrapper pour le contexte Flask
    def run_ebb_flow():
        with app.app_context():
            evaluate_ebb_and_flow()

    def run_sensors():
        with app.app_context():
            process_sensor_data()

    def run_hourly_reports():
        with app.app_context():
            notification_service.send_hourly_report()

    # Configurer et démarrer le scheduler
    scheduler.add_job(
        id='ebb_and_flow_job',
        func=run_ebb_flow,
        trigger='interval',
        seconds=10  # Évaluer toutes les 10 secondes pour le dev
    )
    scheduler.add_job(
        id='sensors_job',
        func=run_sensors,
        trigger='interval',
        seconds=5  # Lire les capteurs toutes les 5 secondes
    )
    scheduler.add_job(
        id='hourly_report_job',
        func=run_hourly_reports,
        trigger='cron',
        minute=0  # Exécuter à la minute 0 de chaque heure (toutes les heures)
    )
    scheduler.start()

    return app


# --- WebSocket events ---
@socketio.on("connect")
def handle_connect():
    print("Client WebSocket connecté")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client WebSocket déconnecté")


if __name__ == "__main__":
    app = create_app()
    print(f"Serre Hydroponique API démarrée sur http://{app.config['HOST']}:{app.config['PORT']}")
    socketio.run(
        app,
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
        allow_unsafe_werkzeug=True,
    )
