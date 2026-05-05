"""
Extensions Flask — initialisées ici, liées à l'app dans app.py
Cela évite les imports circulaires.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_apscheduler import APScheduler

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")
cors = CORS()
scheduler = APScheduler()
