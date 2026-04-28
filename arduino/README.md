# 🔌 Arduino Firmware — Serre Hydroponique

Firmware pour Arduino Uno qui lit les capteurs réels et contrôle les actionneurs via des commandes série envoyées par le backend Flask.

---

## 📦 Bibliothèques Requises

Installez ces bibliothèques via **Arduino IDE → Outils → Gérer les bibliothèques** :

| Bibliothèque | Auteur | Usage |
|---------------|--------|-------|
| **DHT sensor library** | Adafruit | Lecture du DHT11 (temp air + humidité) |
| **OneWire** | Paul Stoffregen | Protocole OneWire pour le DS18B20 |
| **DallasTemperature** | Miles Burton | Lecture simplifiée du DS18B20 |

> **Note :** La bibliothèque DHT d'Adafruit nécessite aussi **Adafruit Unified Sensor** — elle sera installée automatiquement.

---

## 🔧 Câblage Résumé

### Capteurs

| Capteur | Pin | Notes |
|---------|-----|-------|
| DHT11 | D4 | Data pin, résistance pull-up 10kΩ recommandée |
| DS18B20 | D5 | Résistance pull-up 4.7kΩ entre Data et VCC |
| DFRobot SEN0244 (EC) | A0 | Sortie analogique directe |
| LDR (Photoresistor) | A1 | Diviseur de tension : `5V → LDR → A1 → 10kΩ → GND` |
| Robodo SEN18 (Niveau) | A2 | Sortie analogique directe |

### Actionneurs (Relais active-LOW)

| Relais | Pin | Actionneur |
|--------|-----|------------|
| Module 1 – IN2 | D7 | Ventilateur 12 V |
| Module 1 – IN3 | D8 | Pompe Évacuation 12 V |
| Module 1 – IN4 | D9 | Pompe Alimentation 12 V |
| Module 2 – IN1 | D10 | Lampe 220 V |

---

## 📡 Protocole Série (9600 baud)

### Arduino → PC (Données capteurs)
```
SENSORS|niveau_eau:2.3|temp_eau:22.1|EC:1200|temp_air:25.4|humidite:62.0|luminosite:850
```

### PC → Arduino (Commandes actionneurs)
```
PUMP_IN:1     → Allumer pompe alimentation
PUMP_IN:0     → Éteindre pompe alimentation
PUMP_OUT:1    → Allumer pompe évacuation
PUMP_OUT:0    → Éteindre pompe évacuation
LED:1         → Allumer lampe
LED:0         → Éteindre lampe
FAN:1         → Allumer ventilateur
FAN:0         → Éteindre ventilateur
```

### Arduino → PC (Accusés de réception)
```
ACK:PUMP_IN_ON / ACK:PUMP_IN_OFF
ACK:PUMP_OUT_ON / ACK:PUMP_OUT_OFF
ACK:LED_ON / ACK:LED_OFF
ACK:FAN_ON / ACK:FAN_OFF
```

---

## ⚙️ Calibration

### EC Sensor (SEN0244)
Le coefficient `EC_K_VALUE` dans le code est à `1.0` par défaut. Pour calibrer :
1. Plongez le capteur dans une solution EC connue (ex: 1413 µS/cm).
2. Notez la valeur affichée sur le moniteur série.
3. Ajustez `EC_K_VALUE = valeur_affichée / valeur_réelle`.

### Niveau d'eau (SEN18)
`WATER_LEVEL_MAX_CM` est réglé à `4.0` cm (longueur active du capteur). Ajustez si votre installation est différente.

### LDR
La formule Lux est une approximation (±30%) basée sur un LDR GL5528. Si vous utilisez un autre modèle, ajustez les constantes dans `readLuxFromLDR()`.
