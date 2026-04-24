// ---------------------------------------------------------
// Serre Hydroponique Urbaine Intelligente - Arduino Firmware
// ---------------------------------------------------------

// --- Pins Configuration (Relais 4 Canaux) ---
const int PIN_PUMP_IN = 7;     // Relais 1 - Pompe Alimentation
const int PIN_PUMP_OUT = 8;    // Relais 2 - Pompe Évacuation
const int PIN_LED_GROW = 9;    // Relais 3 - Éclairage LED
const int PIN_FAN = 10;        // Relais 4 - Ventilateur

// --- Capteurs ---
// Note: Certains capteurs nécessitent des bibliothèques (DHT, DallasTemperature, BH1750)
// Ici nous gardons la structure de lecture brute pour l'intégration.
const int PIN_WATER_LEVEL_TRIG = 2; // HC-SR04 Trig
const int PIN_WATER_LEVEL_ECHO = 3; // HC-SR04 Echo
const int PIN_DHT = 4;              // DHT22 Data
const int PIN_DS18B20 = 5;          // DS18B20 Data (OneWire)
const int PIN_EC_SENSOR = A0;       // EC/TDS Analog
// BH1750 utilise I2C (SDA/SCL) - A4/A5 sur Uno

// --- State ---
bool pumpInState = false;
bool pumpOutState = false;
bool ledState = false;
bool fanState = false;

// --- Timing ---
unsigned long lastSensorReadTime = 0;
const unsigned long SENSOR_INTERVAL = 5000; 

void setup() {
  Serial.begin(9600);
  
  pinMode(PIN_PUMP_IN, OUTPUT);
  pinMode(PIN_PUMP_OUT, OUTPUT);
  pinMode(PIN_LED_GROW, OUTPUT);
  pinMode(PIN_FAN, OUTPUT);
  
  digitalWrite(PIN_PUMP_IN, LOW);
  digitalWrite(PIN_PUMP_OUT, LOW);
  digitalWrite(PIN_LED_GROW, LOW);
  digitalWrite(PIN_FAN, LOW);

  Serial.println("ARDUINO_READY");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }

  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorReadTime >= SENSOR_INTERVAL) {
    lastSensorReadTime = currentMillis;
    readAndSendSensors();
  }
}

void processCommand(String cmd) {
  if (cmd == "PUMP_IN:1") {
    pumpInState = true;
    digitalWrite(PIN_PUMP_IN, HIGH);
    Serial.println("ACK:PUMP_IN_ON");
  } 
  else if (cmd == "PUMP_IN:0") {
    pumpInState = false;
    digitalWrite(PIN_PUMP_IN, LOW);
    Serial.println("ACK:PUMP_IN_OFF");
  }
  else if (cmd == "PUMP_OUT:1") {
    pumpOutState = true;
    digitalWrite(PIN_PUMP_OUT, HIGH);
    Serial.println("ACK:PUMP_OUT_ON");
  }
  else if (cmd == "PUMP_OUT:0") {
    pumpOutState = false;
    digitalWrite(PIN_PUMP_OUT, LOW);
    Serial.println("ACK:PUMP_OUT_OFF");
  }
  else if (cmd == "LED:1") {
    ledState = true;
    digitalWrite(PIN_LED_GROW, HIGH);
    Serial.println("ACK:LED_ON");
  }
  else if (cmd == "LED:0") {
    ledState = false;
    digitalWrite(PIN_LED_GROW, LOW);
    Serial.println("ACK:LED_OFF");
  }
  else if (cmd == "FAN:1") {
    fanState = true;
    digitalWrite(PIN_FAN, HIGH);
    Serial.println("ACK:FAN_ON");
  }
  else if (cmd == "FAN:0") {
    fanState = false;
    digitalWrite(PIN_FAN, LOW);
    Serial.println("ACK:FAN_OFF");
  }
  else {
    Serial.print("ERR:UNKNOWN_COMMAND:");
    Serial.println(cmd);
  }
}

void readAndSendSensors() {
  // --- Simulation des lectures (à remplacer par les bibliothèques réelles) ---
  float waterLevelCm = random(10, 45); // HC-SR04
  float tempEau = random(20, 24);    // DS18B20
  float ecVal = random(800, 1500);   // EC TDS
  float tempAir = random(22, 28);    // DHT22
  float humidite = random(40, 70);   // DHT22
  float lux = random(500, 2000);     // BH1750

  // Format: SENSORS|niveau_eau:X|temp_eau:X|EC:X|temp_air:X|humidite:X|luminosite:X
  Serial.print("SENSORS|");
  Serial.print("niveau_eau:"); Serial.print(waterLevelCm); Serial.print("|");
  Serial.print("temp_eau:"); Serial.print(tempEau); Serial.print("|");
  Serial.print("EC:"); Serial.print(ecVal); Serial.print("|");
  Serial.print("temp_air:"); Serial.print(tempAir); Serial.print("|");
  Serial.print("humidite:"); Serial.print(humidite); Serial.print("|");
  Serial.print("luminosite:"); Serial.println(lux);
}
