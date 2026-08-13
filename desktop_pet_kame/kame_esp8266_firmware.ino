/*
 =============================================================================
 desktop_pet_kame — ESP8266 NodeMCU Firmware (Kame Robot)
 =============================================================================
 2026 Sürümü — Jarvis'in masadaki evcil hayvanı

 🔒 LOKAL İZOLASYON:
    Bu firmware ÇİN BULUTU'na bağlanmaz. Sadece yerel MQTT broker'a
    (GL-MT3000) bağlanır. Hiçbir dış sunucuya istek göndermez.

 🧠 "BEYİNSİZ GÖVDE":
    Kame'nin kamera/mikrofonu YOK. Tüm zeka Jarvis'ten (Cloud VPS)
    MQTT komutları olarak gelir. Kame sadece komutları uygular.

 📡 MQTT TOPIC'LERİ (Dinler):
    kame/command/move   → {"dir": "forward", "steps": 3}
    kame/command/dance  → {"bpm": 120, "beat": 1}
    kame/command/pose    → {"pose": "bow"}
    kame/command/sit     → çömel
    kame/command/stand   → kalk

 📡 MQTT TOPIC'LERİ (Gönderir):
    kame/status/battery → {"level": 85}
    kame/status/alive   → {"heartbeat": 1}

 GEREKLİ KÜTÜPHANELER:
    Arduino IDE → Library Manager:
    - PubSubClient (MQTT)
    - ESP8266WiFi (dahili)

 =============================================================================
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Servo.h>
#include <ArduinoJson.h>

// =============================================================================
// KONFIGÜRASYON
// =============================================================================

// WiFi — Sadece yerel ağ (GL-MT3000)
const char* WIFI_SSID = "GL-MT3000";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT — Yerel broker (ÇİN BULUTU YOK!)
const char* MQTT_BROKER = "gl-mt3000.local";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "kame-desktop-pet";

// Servo pin'leri (ESP8266 NodeMCU)
// D1=GPIO5, D2=GPIO4, D3=GPIO0, D4=GPIO2
// D5=GPIO14, D6=GPIO12, D7=GPIO13, D8=GPIO15
const int SERVO_PINS[8] = {D1, D2, D3, D4, D5, D6, D7, D8};

// Servo kanal eşlemesi
// 0: Sol Ön Hip, 1: Sol Ön Knee
// 2: Sağ Ön Hip, 3: Sağ Ön Knee
// 4: Sol Arka Hip, 5: Sol Arka Knee
// 6: Sağ Arka Hip, 7: Sağ Arka Knee

// Servo orta pozisyon (derece)
const int SERVO_CENTER[8] = {90, 90, 90, 90, 90, 90, 90, 90};

// Hareket parametreleri
const int SERVO_MIN = 30;
const int SERVO_MAX = 150;
const int WALK_SPEED = 3;      // derece/adım
const int DANCE_SPEED = 5;     // derece/adım (dans daha hızlı)

// Batarya ölçüm (Analog A0 pin)
const int BATTERY_PIN = A0;
const float BATTERY_FULL = 840;   // 2S LiPo tam = 8.4V → A0 ~840
const float BATTERY_EMPTY = 660;  // 2S LiPo boş = 6.6V → A0 ~660

// =============================================================================
// GLOBAL DEĞİŞKENLER
// =============================================================================

Servo servos[8];
WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastHeartbeat = 0;
unsigned long lastBatteryCheck = 0;
int currentPose[8] = {90, 90, 90, 90, 90, 90, 90, 90};

// Dans durumu
bool dancing = false;
int danceBpm = 120;
int danceBeat = 0;
unsigned long lastBeatTime = 0;

// =============================================================================
// KURULUM
// =============================================================================

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Kame Desktop Pet ===");

  // Servo'ları başlat
  for (int i = 0; i < 8; i++) {
    servos[i].attach(SERVO_PINS[i]);
    servos[i].write(SERVO_CENTER[i]);
    currentPose[i] = SERVO_CENTER[i];
  }
  Serial.println("8 servo başlatıldı");

  // WiFi bağlan
  WiFi.mode(WIFI_STA);  // Sadece istemci (AP kapalı)
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("WiFi bağlanıyor");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi bağlandı: " + WiFi.localIP().toString());

  // MQTT kur
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  mqtt.setBufferSize(512);

  // mDNS (kame.local)
  // Arduino IDE → ESP8266 mDNS kütüphanesi gerekli

  Serial.println("Kame hazır — MQTT bekleniyor...");
}

// =============================================================================
// ANA DÖNGÜ
// =============================================================================

void loop() {
  // MQTT bağlantısı维持
  if (!mqtt.connected()) {
    mqttReconnect();
  }
  mqtt.loop();

  // Heartbeat (her 5 sn)
  if (millis() - lastHeartbeat > 5000) {
    lastHeartbeat = millis();
    mqtt.publish("kame/status/alive", "{\"heartbeat\":1}");
  }

  // Batarya kontrolü (her 30 sn)
  if (millis() - lastBatteryCheck > 30000) {
    lastBatteryCheck = millis();
    checkBattery();
  }

  // Dans modu aktifse ritim beklet
  if (dancing) {
    danceLoop();
  }
}

// =============================================================================
// MQTT
// =============================================================================

void mqttReconnect() {
  while (!mqtt.connected()) {
    Serial.print("MQTT bağlanıyor: ");
    if (mqtt.connect(MQTT_CLIENT_ID)) {
      Serial.println("bağlandı");
      mqtt.subscribe("kame/command/move");
      mqtt.subscribe("kame/command/dance");
      mqtt.subscribe("kame/command/pose");
      mqtt.subscribe("kame/command/sit");
      mqtt.subscribe("kame/command/stand");
      mqtt.publish("kame/status/alive", "{\"heartbeat\":1}");
    } else {
      Serial.print("hata, rc=");
      Serial.print(mqtt.state());
      delay(2000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.println("JSON parse hatası");
    return;
  }

  String topicStr = String(topic);
  Serial.print("MQTT: ");
  Serial.println(topicStr);

  if (topicStr == "kame/command/move") {
    String dir = doc["dir"] | "forward";
    int steps = doc["steps"] | 1;
    moveRobot(dir, steps);
  }
  else if (topicStr == "kame/command/dance") {
    danceBpm = doc["bpm"] | 120;
    danceBeat = doc["beat"] | 0;
    dancing = true;
    lastBeatTime = millis();
  }
  else if (topicStr == "kame/command/pose") {
    String pose = doc["pose"] | "bow";
    strikePose(pose);
  }
  else if (topicStr == "kame/command/sit") {
    sitDown();
  }
  else if (topicStr == "kame/command/stand") {
    standUp();
  }
}

// =============================================================================
// HAREKET FONKSİYONLARI
// =============================================================================

void moveServo(int channel, int angle) {
  angle = constrain(angle, SERVO_MIN, SERVO_MAX);
  // Yumuşak hareket
  int from = currentPose[channel];
  int to = angle;
  int step = (to > from) ? 1 : -1;
  for (int a = from; a != to; a += step) {
    servos[channel].write(a);
    delayMicroseconds(500);  // 0.5ms per derece → ~90ms for 180°
  }
  servos[channel].write(to);
  currentPose[channel] = to;
}

void moveAllServos(int angles[8]) {
  for (int i = 0; i < 8; i++) {
    moveServo(i, angles[i]);
  }
}

// --- STAND (Dik Dur) ---
void standUp() {
  Serial.println("Kalk");
  int pose[8] = {90, 90, 90, 90, 90, 90, 90, 90};
  moveAllServos(pose);
}

// --- SIT (Çömel) ---
void sitDown() {
  Serial.println("Çömel");
  // Ön bacaklar dik, arka bacaklar bükülü
  int pose[8] = {90, 90, 90, 90, 70, 110, 70, 110};
  moveAllServos(pose);
  dancing = false;
}

// --- WALK (Yürü) ---
void moveRobot(String dir, int steps) {
  Serial.println("Yürü: " + dir + " " + String(steps) + " adım");
  dancing = false;

  for (int s = 0; s < steps; s++) {
    if (dir == "forward") {
      walkForward();
    } else if (dir == "backward") {
      walkBackward();
    } else if (dir == "left") {
      turnLeft();
    } else if (dir == "right") {
      turnRight();
    }
    delay(100);
  }
}

// Diagonal gait — sol ön + sağ arka, sonra sağ ön + sol arka
void walkForward() {
  // Faz 1: Sol ön + sağ arka yukarı ve ileri
  moveServo(0, 110);  // Sol ön hip ileri
  moveServo(1, 70);   // Sol ön knee yukarı
  moveServo(6, 110);  // Sağ arka hip ileri
  moveServo(7, 70);   // Sağ arka knee yukarı
  delay(150);

  // Faz 2: Sağ ön + sol arka yukarı ve ileri
  moveServo(2, 110);  // Sağ ön hip ileri
  moveServo(3, 70);   // Sağ ön knee yukarı
  moveServo(4, 110);  // Sol arka hip ileri
  moveServo(5, 70);   // Sol arka knee yukarı
  delay(150);

  // Merkez
  standUp();
}

void walkBackward() {
  // Ters yön
  moveServo(0, 70); moveServo(1, 110);
  moveServo(6, 70); moveServo(7, 110);
  delay(150);
  moveServo(2, 70); moveServo(3, 110);
  moveServo(4, 70); moveServo(5, 110);
  delay(150);
  standUp();
}

void turnLeft() {
  // Sol bacaklar geri, sağ bacaklar ileri
  moveServo(0, 70); moveServo(4, 70);
  moveServo(2, 110); moveServo(6, 110);
  delay(200);
  standUp();
}

void turnRight() {
  moveServo(0, 110); moveServo(4, 110);
  moveServo(2, 70); moveServo(6, 70);
  delay(200);
  standUp();
}

// --- DANCE (Dans) ---
// Müzik BPM'ine göre senkron çömelme + ayak vurma
void danceLoop() {
  // BPM → beat süresi (ms)
  float beatInterval = 60000.0 / danceBpm;  // 120 BPM → 500ms

  if (millis() - lastBeatTime > beatInterval) {
    lastBeatTime = millis();
    danceBeat++;

    if (danceBeat % 2 == 0) {
      // Çift beat: çömel (bass drop)
      int pose[8] = {80, 100, 80, 100, 80, 100, 80, 100};
      moveAllServos(pose);
    } else {
      // Tek beat: kalk + ayak vuru
      int pose[8] = {100, 80, 100, 80, 100, 80, 100, 80};
      moveAllServos(pose);
    }

    // 4 beat'te bir "spin" (dönüş)
    if (danceBeat % 8 == 0) {
      turnLeft();
    }
  }
}

// --- POSE (Poz Ver) ---
void strikePose(String pose) {
  Serial.println("Poz: " + pose);
  dancing = false;

  if (pose == "bow") {
    // Baş eğme — ön bacaklar uzat, gövde alçalt
    moveServo(0, 120);  // Sol ön hip ileri
    moveServo(1, 60);   // Sol ön knee uzat
    moveServo(2, 120);  // Sağ ön hip ileri
    moveServo(3, 60);   // Sağ ön knee uzat
    moveServo(4, 70);   // Sol arka hip geri
    moveServo(5, 110);  // Sol arka knee bük
    moveServo(6, 70);   // Sağ arka hip geri
    moveServo(7, 110);  // Sağ arka knee bük
    delay(1000);
    standUp();
  }
  else if (pose == "wave") {
    // Tek ön bacak kaldır
    moveServo(1, 30);  // Sol ön knee yukarı kaldır
    delay(500);
    for (int i = 0; i < 3; i++) {
      moveServo(0, 70);
      delay(200);
      moveServo(0, 110);
      delay(200);
    }
    standUp();
  }
  else if (pose == "tilt") {
    // Gövde yana eğ
    moveServo(0, 100); moveServo(2, 80);
    moveServo(4, 100); moveServo(6, 80);
    delay(500);
    standUp();
  }
}

// =============================================================================
// BATARYA
// =============================================================================

void checkBattery() {
  int raw = analogRead(BATTERY_PIN);
  float level = map(raw, (int)BATTERY_EMPTY, (int)BATTERY_FULL, 0, 100);
  level = constrain(level, 0, 100);

  String payload = "{\"level\":" + String((int)level) + "}";
  mqtt.publish("kame/status/battery", payload.c_str());

  Serial.println("Batarya: " + String((int)level) + "%");

  // Şarj azsa uyar
  if (level < 20) {
    mqtt.publish("kame/status/battery", "{\"level\":0,\"low\":true}");
  }
}