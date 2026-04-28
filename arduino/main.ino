// =============================================================
//  Serre Hydroponique Urbaine Intelligente — Arduino Firmware
//  ---------------------------------------------------------
//  Real sensor readings + serial command protocol for the
//  Flask backend (serial_service.py / decision_engine.py).
//
//  SENSORS:
//    - DHT11            → Temp air + Humidité    (Digital, Pin 3)
//    - DS18B20          → Temp eau               (OneWire, Pin 2)
//    - DFRobot SEN0244  → EC (temp-compensated)  (Analog,  A0)
//    - LDR / Photoresistor → Luminosité (≈ Lux)  (Analog,  A1)
//    - Robodo SEN18     → Niveau eau (depth)      (Analog,  A2)
//
//  ACTUATORS (2× relay modules, active-LOW):
//    Module 1:
//      IN2 → Ventilateur 12 V        (Pin 7)
//      IN3 → Pompe Évacuation 12 V   (Pin 6)
//      IN4 → Pompe Alimentation 12 V (Pin 5)
//    Module 2:
//      IN1 → Lampe 220 V             (Pin 4)
//
//  SERIAL PROTOCOL (9600 baud):
//    Arduino → PC :  SENSORS|niveau_eau:X|temp_eau:X|EC:X|temp_air:X|humidite:X|luminosite:X
//    PC → Arduino :  PUMP_IN:1 / PUMP_IN:0 / PUMP_OUT:1 / PUMP_OUT:0
//                    LED:1 / LED:0 / FAN:1 / FAN:0
//    Arduino → PC :  ACK:PUMP_IN_ON / ACK:PUMP_IN_OFF / etc.
// =============================================================

// ─── Libraries ─────────────────────────────────────────────
#include <DHT.h>              // DHT sensor library (by Adafruit)
#include <OneWire.h>          // OneWire protocol
#include <DallasTemperature.h> // DS18B20 helper

// ─── Pin Definitions ───────────────────────────────────────
// Sensors
#define PIN_DHT          3     // DHT11 data pin
#define PIN_DS18B20      2     // DS18B20 data pin (OneWire)
#define PIN_EC_SENSOR    A0    // DFRobot SEN0244 analog out
#define PIN_LDR          A1    // LDR photoresistor (voltage divider)
#define PIN_WATER_LEVEL  A2    // Robodo SEN18 analog out

// Actuators (relay modules — active-LOW)
#define PIN_FAN          7     // Relay Module 1 – IN2: Ventilateur 12 V
#define PIN_PUMP_OUT     6     // Relay Module 1 – IN3: Pompe Évacuation 12 V
#define PIN_PUMP_IN      5     // Relay Module 1 – IN4: Pompe Alimentation 12 V
#define PIN_LED_GROW     4    // Relay Module 2 – IN1: Lampe 220 V

// ─── Constants ─────────────────────────────────────────────
// DHT
#define DHT_TYPE DHT11

// LDR voltage divider
// Wiring: 5V ─── [LDR] ─── A1 ─── [R_FIXED] ─── GND
#define LDR_R_FIXED 10000.0   // 10 kΩ pull-down resistor
#define V_REF       5.0       // Arduino reference voltage

// EC sensor (DFRobot SEN0244)
// Calibration coefficient — tune this with a known EC solution
// Default from DFRobot wiki: K ≈ 1.0
#define EC_K_VALUE  1.0

// Water level sensor (Robodo SEN18)
// Maps the analog range to a depth in cm.
// Adjust WATER_LEVEL_MAX_CM to match the sensor's submerged depth.
#define WATER_LEVEL_MAX_CM  4.0   // Sensor active length ≈ 4 cm

// Timing
#define SENSOR_INTERVAL 5000  // ms between sensor readings

// Relay logic helpers (active-LOW relays)
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

// ─── Forward Declarations ──────────────────────────────────
void processCommand(String cmd);
void readAndSendSensors();
float readWaterLevelCm();
float readDS18B20();
float readEcCompensated(float waterTempC);
float readLuxFromLDR();

// ============================================================
//  SETUP
// ============================================================
void setup() {
  Serial.begin(9600);

  // ── Initialise sensors ──
  dht.begin();
  ds18b20.begin();

  // ── Initialise relay pins (OFF = HIGH for active-LOW) ──
  pinMode(PIN_PUMP_IN,  OUTPUT);
  pinMode(PIN_PUMP_OUT, OUTPUT);
  pinMode(PIN_LED_GROW, OUTPUT);
  pinMode(PIN_FAN,      OUTPUT);

  digitalWrite(PIN_PUMP_IN,  RELAY_OFF);
  digitalWrite(PIN_PUMP_OUT, RELAY_OFF);
  digitalWrite(PIN_LED_GROW, RELAY_OFF);
  digitalWrite(PIN_FAN,      RELAY_OFF);

  // ── Sensor input pins ──
  // Analog pins default to input, but be explicit
  pinMode(PIN_EC_SENSOR,   INPUT);
  pinMode(PIN_LDR,         INPUT);
  pinMode(PIN_WATER_LEVEL, INPUT);

  // Signal readiness to the backend
  Serial.println("ARDUINO_READY");
}

// ============================================================
//  MAIN LOOP
// ============================================================
void loop() {
  // ── Handle incoming serial commands from the backend ──
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }

  // ── Periodic sensor readings ──
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorReadTime >= SENSOR_INTERVAL) {
    lastSensorReadTime = currentMillis;
    readAndSendSensors();
  }
}

// ============================================================
//  COMMAND PROCESSOR
//  Receives commands from the backend and toggles relays.
//  Format: "ACTUATOR:STATE"  (STATE = 1 ON, 0 OFF)
// ============================================================
void processCommand(String cmd) {

  // ── Pompe Alimentation (Pump feeding water IN) ──
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

  // ── Pompe Évacuation (Pump draining water OUT) ──
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

  // ── Lampe / Éclairage (220 V lamp via relay) ──
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

  // ── Ventilateur (12 V Fan) ──
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

  // ── Unknown ──
  else {
    Serial.print("ERR:UNKNOWN_COMMAND:");
    Serial.println(cmd);
  }
}

// ============================================================
//  SENSOR READINGS  —  Read all sensors and send to backend
// ============================================================
void readAndSendSensors() {

  // 1. DHT11 — Air temperature & humidity
  float humidite = dht.readHumidity();
  float tempAir  = dht.readTemperature(); // Celsius

  // Guard against NaN from DHT read failures
  if (isnan(humidite)) humidite = -1.0;
  if (isnan(tempAir))  tempAir  = -1.0;

  // 2. DS18B20 — Water temperature
  float tempEau = readDS18B20();

  // 3. DFRobot SEN0244 — EC (temperature-compensated)
  float ecVal = readEcCompensated(tempEau);

  // 4. LDR — Estimated Lux
  float lux = readLuxFromLDR();

  // 5. Robodo SEN18 — Water level (cm)
  float waterLevelCm = readWaterLevelCm();

  // ── Build & send the data string ──
  // Format: SENSORS|niveau_eau:X|temp_eau:X|EC:X|temp_air:X|humidite:X|luminosite:X
  Serial.print("SENSORS|");
  Serial.print("niveau_eau:");  Serial.print(waterLevelCm, 1); Serial.print("|");
  Serial.print("temp_eau:");    Serial.print(tempEau, 1);       Serial.print("|");
  Serial.print("EC:");          Serial.print(ecVal, 0);         Serial.print("|");
  Serial.print("temp_air:");    Serial.print(tempAir, 1);       Serial.print("|");
  Serial.print("humidite:");    Serial.print(humidite, 1);      Serial.print("|");
  Serial.print("luminosite:");  Serial.println(lux, 0);
}

// ============================================================
//  INDIVIDUAL SENSOR FUNCTIONS
// ============================================================

// ─── DS18B20 — Waterproof temperature probe ────────────────
float readDS18B20() {
  ds18b20.requestTemperatures();
  float tempC = ds18b20.getTempCByIndex(0);

  // DEVICE_DISCONNECTED_C is -127
  if (tempC == DEVICE_DISCONNECTED_C || tempC < -50.0) {
    return -1.0; // Sensor error
  }
  return tempC;
}

// ─── DFRobot SEN0244 — EC with temperature compensation ───
//  The raw voltage → EC conversion uses the DFRobot formula:
//    voltage   = ADC × (Vref / 1024)
//    rawEC     = (voltage / K)  × 1000        (µS/cm)
//    compEC    = rawEC / (1 + 0.0185 × (T − 25))
//  The 0.0185 coefficient is the standard NaCl temperature
//  compensation factor.
// ────────────────────────────────────────────────────────────
float readEcCompensated(float waterTempC) {
  // Average multiple ADC samples for stability
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(PIN_EC_SENSOR);
    delay(5);
  }
  float avgADC = sum / 10.0;

  float voltage = avgADC * (V_REF / 1024.0);

  // Raw EC in µS/cm (K calibration coefficient)
  float rawEC = (voltage / EC_K_VALUE) * 1000.0;

  // Temperature compensation (default to 25 °C if sensor failed)
  float refTemp = (waterTempC > 0) ? waterTempC : 25.0;
  float compensatedEC = rawEC / (1.0 + 0.0185 * (refTemp - 25.0));

  // Clamp to a sane range
  if (compensatedEC < 0)    compensatedEC = 0;
  if (compensatedEC > 5000) compensatedEC = 5000;

  return compensatedEC;
}

// ─── LDR — Photoresistor → estimated Lux ──────────────────
//  Wiring: 5V ── [LDR] ── A1 ── [10kΩ] ── GND
//
//  Calculations:
//    V_out  = ADC × (5 / 1024)
//    R_LDR  = R_fixed × (V_ref − V_out) / V_out
//    Lux    ≈ 325 × (R_LDR / 1000)^(−0.8)
//
//  This empirical formula is calibrated for a GL5528 LDR.
//  Accuracy is ±30 % — sufficient for grow-light automation.
// ────────────────────────────────────────────────────────────
float readLuxFromLDR() {
  int adc = analogRead(PIN_LDR);

  // Prevent division by zero
  if (adc == 0) adc = 1;

  float vOut = adc * (V_REF / 1024.0);
  float rLDR = LDR_R_FIXED * (V_REF - vOut) / vOut;

  // Empirical Lux approximation (GL5528)
  float lux = 325.0 * pow(rLDR / 1000.0, -0.8);

  // Clamp
  if (lux < 0)      lux = 0;
  if (lux > 100000)  lux = 100000;

  return lux;
}

// ─── Robodo SEN18 — Analog water level sensor ──────────────
//  The sensor outputs 0 V (dry) to ≈4.2 V (fully submerged).
//  We map the ADC range linearly to 0 .. WATER_LEVEL_MAX_CM.
//
//  ⚠ WATER_LEVEL_MAX_CM should match the physical length of
//    the sensor's active conductive area (typically ~4 cm).
//    Adjust if your sensor / installation differs.
// ────────────────────────────────────────────────────────────
float readWaterLevelCm() {
  // Average a few samples to reduce noise
  long sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += analogRead(PIN_WATER_LEVEL);
    delay(2);
  }
  float avgADC = sum / 5.0;

  // Map ADC (0-1023) to depth (0 - MAX cm)
  float depth = (avgADC / 1023.0) * WATER_LEVEL_MAX_CM;

  // Clamp
  if (depth < 0)                   depth = 0;
  if (depth > WATER_LEVEL_MAX_CM)  depth = WATER_LEVEL_MAX_CM;

  return depth;
}
