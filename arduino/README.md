# 🔌 Firmware Arduino - Serre Hydroponique

Ce dossier contient le code C++ pour la carte Arduino Uno pilotant la serre.

## 🛠️ Configuration Matérielle

### Branchement des Actionneurs (Relais 5V)
- **Pin 7** : Pompe d'Alimentation
- **Pin 8** : Pompe d'Évacuation
- **Pin 9** : Éclairage LED (Grow Light)
- **Pin 10** : Ventilateur

### Branchement des Capteurs
- **HC-SR04** (Niveau d'eau) : Trig (Pin 2), Echo (Pin 3)
- **DHT22** (Air) : Data (Pin 4)
- **DS18B20** (Eau) : Data (Pin 5)
- **Capteur EC** : Analog A0
- **BH1750** (Luminosité) : I2C (SDA/SCL)

## 📡 Communication Série
L'Arduino communique avec le serveur PC via USB à **9600 bauds**.

### Format des données envoyées (Sortie)
Toutes les 5 secondes, l'Arduino envoie une chaîne formatée :
`SENSORS|niveau_eau:X|temp_eau:X|EC:X|temp_air:X|humidite:X|luminosite:X`

### Format des commandes reçues (Entrée)
L'Arduino écoute les commandes suivantes :
- `PUMP_IN:1` / `PUMP_IN:0`
- `PUMP_OUT:1` / `PUMP_OUT:0`
- `LED:1` / `LED:0`
- `FAN:1` / `FAN:0`

## 🚀 Installation
1. Ouvrez `main.ino` dans l'Arduino IDE.
2. Installez les bibliothèques nécessaires (DHT, OneWire, DallasTemperature, BH1750) via le gestionnaire de bibliothèques.
3. Téléversez sur votre Arduino Uno.
