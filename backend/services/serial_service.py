import serial
import time
import threading
from flask import current_app

class SerialService:
    def __init__(self):
        self.serial_connection = None
        self.is_connected = False
        self.mock_mode = False
        self._lock = threading.Lock()

    def connect(self, port, baudrate=9600):
        """Établit la connexion avec l'Arduino."""
        try:
            print(f"[Serial Service] Tentative de connexion sur {port} à {baudrate} bauds...")
            self.serial_connection = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2) # Attente de la réinitialisation de l'Arduino
            self.is_connected = True
            print("[Serial Service] Connecté avec succès à l'Arduino.")
        except serial.SerialException as e:
            print(f"[Serial Service] Échec de la connexion série: {e}")
            print("[Serial Service] Passage en mode SIMULATION (Mock Mode).")
            self.is_connected = False
            self.mock_mode = True

    def send_command(self, command):
        """Envoie une commande à l'Arduino."""
        with self._lock:
            if self.is_connected and self.serial_connection:
                try:
                    # L'Arduino s'attend à une commande terminée par \n
                    full_command = f"{command}\n"
                    self.serial_connection.write(full_command.encode('utf-8'))
                    print(f"[Serial Service] Commande envoyée: {command}")
                    return True
                except Exception as e:
                    print(f"[Serial Service] Erreur lors de l'envoi de la commande: {e}")
                    return False
            elif self.mock_mode:
                print(f"[Serial Service - MOCK] Commande simulée envoyée: {command}")
                return True
            else:
                print("[Serial Service] Non connecté.")
                return False

    def read_data(self):
        """Lit les données envoyées par l'Arduino."""
        if self.is_connected and self.serial_connection:
            if self.serial_connection.in_waiting > 0:
                try:
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    return data
                except Exception as e:
                    print(f"[Serial Service] Erreur de lecture: {e}")
                    return None
        elif self.mock_mode:
            # En mode mock, on pourrait renvoyer des fausses données périodiquement
            pass
        return None

    def close(self):
        """Ferme la connexion série."""
        if self.serial_connection and self.is_connected:
            self.serial_connection.close()
            self.is_connected = False
            print("[Serial Service] Connexion fermée.")

# Instance globale (Singleton)
serial_service = SerialService()
