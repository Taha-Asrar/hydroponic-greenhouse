import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from extensions import db
from models.alerte import Alerte
from models.notification import Notification
from models.utilisateur import Utilisateur
from datetime import datetime, timedelta, timezone

class NotificationService:
    @staticmethod
    def create_alert(cycle_id, message, severite="warning"):
        """Crée une alerte interne dans la base de données."""
        alerte = Alerte(
            id_cycle=cycle_id,
            message=message,
            severite=severite,
            acquittee=False
        )
        db.session.add(alerte)
        db.session.commit()
        return alerte

    @staticmethod
    def send_email(to_email, subject, body):
        """Envoie un email via SMTP (configuré dans app.config)."""
        # Récupérer la config depuis current_app
        smtp_server = current_app.config.get("SMTP_SERVER")
        smtp_port = current_app.config.get("SMTP_PORT", 587)
        smtp_user = current_app.config.get("SMTP_USERNAME")
        smtp_pass = current_app.config.get("SMTP_PASSWORD")
        from_email = current_app.config.get("NOTIFICATION_EMAIL_FROM")

        if not all([smtp_server, smtp_user, smtp_pass, from_email]):
            print("[Notification Service] Erreur: Configuration SMTP incomplète.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            
            print(f"[Notification Service] Email envoyé à {to_email}")
            return True
        except Exception as e:
            print(f"[Notification Service] Erreur d'envoi email: {e}")
            return False

    @staticmethod
    def send_hourly_report():
        """Récupère les alertes de la dernière heure et envoie un résumé par email."""
        try:
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            alertes = Alerte.query.filter(Alerte.horodatage >= one_hour_ago).all()
            
            if not alertes:
                print("[Notification Service] Aucune alerte dans la dernière heure. Pas d'email.")
                return

            # Destinataires: tous les utilisateurs
            utilisateurs = Utilisateur.query.filter_by(actif=True).all()
            if not utilisateurs:
                print("[Notification Service] Aucun utilisateur actif pour recevoir le rapport.")
                return

            subject = f"[Smart Greenhouse] Rapport d'alertes horaire ({len(alertes)} alertes)"
            
            body = "Bonjour,\n\nVoici le résumé des alertes détectées dans la serre lors de la dernière heure :\n\n"
            for a in alertes:
                body += f"- {a.horodatage.strftime('%H:%M:%S')} | [{a.severite.upper()}] : {a.message}\n"
            
            body += "\nLe système a automatiquement ajusté les actionneurs pour corriger ces problèmes.\n"
            body += "Connectez-vous au dashboard pour plus de détails.\n\nCordialement,\nVotre Serre Intelligente"

            for u in utilisateurs:
                if u.email:
                    NotificationService.send_email(u.email, subject, body)
                    
            print(f"[Notification Service] Rapport horaire envoyé avec succès à {len(utilisateurs)} utilisateur(s).")
        except Exception as e:
            print(f"[Notification Service] Erreur lors de l'envoi du rapport horaire: {e}")

notification_service = NotificationService()
