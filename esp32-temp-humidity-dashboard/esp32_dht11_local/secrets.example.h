// Copy this file to secrets.h (same folder) and fill in your own values.
// secrets.h is listed in .gitignore, so it will NOT be uploaded to GitHub.
#pragma once

#define WIFI_SSID     "YOUR_WIFI_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Use the IPv4 address of the computer running app.py (run "ipconfig" on Windows).
// Do NOT use "localhost": on the ESP32 that would mean the ESP32 itself.
#define SERVER_URL    "http://192.168.1.100:5000/api/data"

#define DEVICE_KEY    "change-this-device-key"   // must match DEVICE_KEY in config.py
