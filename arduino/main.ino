// =============================================================
//  Serre Hydroponique Urbaine Intelligente — Arduino Firmware
//  ---------------------------------------------------------
//  SENSORS:
//    - DHT11            → Temp air + Humidité    (Digital, Pin 3)
//    - DS18B20          → Temp eau               (OneWire, Pin 2)
//    - LDR              → Luminosité (%)         (Analog,  A1)
//    - Robodo SEN18     → Niveau eau (%)         (Analog,  A2)
//
//  ACTUATORS (relay modules):
//    Module 1:
//      IN2 → Ventilateur 12 V        (Pin 7)
//      IN3 → Pompe Évacuation 12 V   (Pin 6)
//      IN4 → Pompe Alimentation 12 V (Pin 5)
//    Module 2:
//      IN1 → Lampe 220 V             (Pin 4)
//
//  SERIAL PROTOCOL (9600 baud):
//    Arduino → PC :  SENSORS|niveau_eau:X|temp_eau:X|temp_air:X|humidite:X|luminosite:X
//    PC → Arduino :  PUMP_IN:1/0 | PUMP_OUT:1/0 | LED:1/0 | FAN:1/0
//    Arduino → PC :  ACK:PUMP_IN_ON / ACK:PUMP_IN_OFF / etc.
// =============================================================

#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ─── Pin Definitions ───────────────────────────────────────
#define PIN_DHT          3
#define PIN_DS18B20      2
#define PIN_LDR          A1
#define PIN_WATER_LEVEL  A2

#define PIN_FAN          7
#define PIN_PUMP_OUT     6
#define PIN_PUMP_IN      5
#define PIN_LED_GROW     4

// ─── Constants ─────────────────────────────────────────────
#define DHT_TYPE DHT11
#define SENSOR_INTERVAL 2000

// Relay logic (active-LOW for most relay modules)
#define RELAY_ON   LOW
#define RELAY_OFF  HIGH

// ─── Sensor Objects ────────────────────────────────────────
DHT dht(PIN_DHT, DHT_TYPE);
OneWire oneWire(PIN_DS18B20);
DallasTemperature ds18b20(&oneWire);

// ─── State ─────────────────────────────────────────────────
bool pumpInState  = false;
bool pumpOutState = false;
bool ledState     = false;
bool fanState     = false;

unsigned long lastSensorReadTime = 0;

// Cache for DHT (retry fallback)
float lastGoodTempAir  = -1.0;
float lastGoodHumidite = -1.0;

// ─── Forward Declarations ──────────────────────────────────
void processCommand(String cmd);
void readAndSendSensors();
float readDS18B20();

// ============================================================
//  SETUP
// ============================================================
void setup() {
  Serial.begin(9600);
  dht.begin();
  ds18b20.begin();

  // Initialiser a l'etat ETEINT AVANT de passer en OUTPUT
  // Tous les relais sont identiques (Active-LOW, donc Eteints = HIGH)
  digitalWrite(PIN_PUMP_IN,  RELAY_OFF);
  digitalWrite(PIN_PUMP_OUT, RELAY_OFF);
  digitalWrite(PIN_FAN,      RELAY_OFF);
  digitalWrite(PIN_LED_GROW, RELAY_OFF);

  pinMode(PIN_PUMP_IN,  OUTPUT);
  pinMode(PIN_PUMP_OUT, OUTPUT);
  pinMode(PIN_LED_GROW, OUTPUT);
  pinMode(PIN_FAN,      OUTPUT);

  pinMode(PIN_LDR, INPUT_PULLUP);
  pinMode(PIN_WATER_LEVEL, INPUT);

  Serial.println("ARDUINO_READY");
}

// ============================================================
//  MAIN LOOP
// ============================================================
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

// ============================================================
//  COMMAND PROCESSOR
// ============================================================
void processCommand(String cmd) {
  if (cmd == "PUMP_IN:1") {
    pumpInState = true;
    digitalWrite(PIN_PUMP_IN, RELAY_ON);
    Serial.println("ACK:PUMP_IN_ON");
  }
  else if (cmd == "PUMP_IN:0") {
    pumpInState = false;
    digitalWrite(PIN_PUMP_IN, RELAY_OFF);
    Serial.println("ACK:PUMP_IN_OFF");
  }
  else if (cmd == "PUMP_OUT:1") {
    pumpOutState = true;
    digitalWrite(PIN_PUMP_OUT, RELAY_ON);
    Serial.println("ACK:PUMP_OUT_ON");
  }
  else if (cmd == "PUMP_OUT:0") {
    pumpOutState = false;
    digitalWrite(PIN_PUMP_OUT, RELAY_OFF);
    Serial.println("ACK:PUMP_OUT_OFF");
  }
  else if (cmd == "LED:1") {
    ledState = true;
    digitalWrite(PIN_LED_GROW, RELAY_ON);
    Serial.println("ACK:LED_ON");
  }
  else if (cmd == "LED:0") {
    ledState = false;
    digitalWrite(PIN_LED_GROW, RELAY_OFF);
    Serial.println("ACK:LED_OFF");
  }
  else if (cmd == "FAN:1") {
    fanState = true;
    digitalWrite(PIN_FAN, RELAY_ON);
    Serial.println("ACK:FAN_ON");
  }
  else if (cmd == "FAN:0") {
    fanState = false;
    digitalWrite(PIN_FAN, RELAY_OFF);
    Serial.println("ACK:FAN_OFF");
  }
  else {
    Serial.print("ERR:UNKNOWN_COMMAND:");
    Serial.println(cmd);
  }
}

// ============================================================
//  SENSOR READINGS
// ============================================================
void readAndSendSensors() {

  // 1. DHT11 — Air temp & humidity (sans retry rapide car ca bloque le DHT11)
  float humidite = -1.0;
  float tempAir  = -1.0;

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  if (!isnan(h) && !isnan(t) && h > 0 && h <= 100 && t > -40 && t < 80) {
    humidite = h;
    tempAir  = t;
    lastGoodTempAir  = t;
    lastGoodHumidite = h;
  } else {
    // Fallback to last good value if reading failed
    if (lastGoodHumidite >= 0) humidite = lastGoodHumidite;
    if (lastGoodTempAir  >= 0) tempAir  = lastGoodTempAir;
  }

  // 2. DS18B20 — Water temperature
  float tempEau = readDS18B20();

  // 3. LDR — Light as percentage (0-100%)
  int ldrADC = analogRead(PIN_LDR);
  float luminosite = (ldrADC / 1023.0) * 100.0;
  if (luminosite < 0)   luminosite = 0;
  if (luminosite > 100) luminosite = 100;

  // 4. Water level — as percentage (0-100%)
  //    Le capteur analogique SEN18 donne generalement max ~700 dans l'eau, pas 1023.
  long wlSum = 0;
  for (int i = 0; i < 5; i++) {
    wlSum += analogRead(PIN_WATER_LEVEL);
    delay(2);
  }
  float wlAvg = wlSum / 5.0;
  float niveauEau = (wlAvg / 700.0) * 100.0; 
  if (niveauEau < 0)   niveauEau = 0;
  if (niveauEau > 100) niveauEau = 100;

  // ── Send data ──
  // Format: SENSORS|niveau_eau:X|temp_eau:X|temp_air:X|humidite:X|luminosite:X
  Serial.print("SENSORS|");
  Serial.print("niveau_eau:");  Serial.print(niveauEau, 1);   Serial.print("|");
  Serial.print("temp_eau:");    Serial.print(tempEau, 1);      Serial.print("|");
  Serial.print("temp_air:");    Serial.print(tempAir, 1);      Serial.print("|");
  Serial.print("humidite:");    Serial.print(humidite, 1);     Serial.print("|");
  Serial.print("luminosite:");  Serial.println(luminosite, 1);
}

// ─── DS18B20 ───────────────────────────────────────────────
float readDS18B20() {
  ds18b20.requestTemperatures();
  float tempC = ds18b20.getTempCByIndex(0);
  if (tempC == DEVICE_DISCONNECTED_C || tempC < -50.0) {
    return -1.0;
  }
  return tempC;
}