/*
  ESP32-S3 + DHT11 -> local Flask server

  Setup:
    1. Copy secrets.example.h to secrets.h (same folder) and fill in your values.
    2. Install the "DHT sensor library" by Adafruit (and Adafruit Unified Sensor).
    3. Board settings in Arduino IDE (ESP32-S3 N16R8):
         Board: ESP32S3 Dev Module | Flash Size: 16MB | PSRAM: OPI PSRAM
         USB CDC On Boot: Disabled (use the USB-UART port) | Serial Monitor: 115200
*/
#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include "secrets.h"   // WIFI_SSID, WIFI_PASSWORD, SERVER_URL, DEVICE_KEY

#define DHTPIN  4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL = 5000;   // milliseconds

void connectWiFi() {
  Serial.print("Connecting to Wi-Fi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected. ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWiFi();
}

void loop() {
  if (millis() - lastSend < SEND_INTERVAL) return;
  lastSend = millis();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi lost, reconnecting...");
    WiFi.disconnect();
    connectWiFi();
    return;
  }

  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) {
    Serial.println("Failed to read from DHT11 sensor!");
    return;
  }

  String body = "{\"temperature\":" + String(t, 1) + ",\"humidity\":" + String(h, 1) + "}";

  HTTPClient http;
  http.setTimeout(4000);
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-KEY", DEVICE_KEY);

  int code = http.POST(body);
  Serial.printf("Temp: %.0f C  Humidity: %.0f %%  -> server replied: %d\n", t, h, code);
  http.end();
}
