"""
ESP32-S3 Temperature and Humidity Monitor - local server

Receives readings from the ESP32 (DHT11 sensor) and shows them on a
login-protected web dashboard. Every reading is also saved to a CSV file.

Run:   python app.py
Open:  http://localhost:5000
"""
import csv
import os
import time
from collections import deque
from functools import wraps

from flask import (Flask, jsonify, redirect, render_template, request,
                   session, url_for)

try:
    import config
except ImportError:
    raise SystemExit(
        "config.py not found.\n"
        "Copy config.example.py to config.py, edit the values, then run again."
    )

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

latest = {"temperature": None, "humidity": None, "time": None}
history = deque(maxlen=50)   # last 50 readings, kept in memory only


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            if request.path.startswith("/api/"):
                return jsonify(error="login required"), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if (request.form.get("username") == config.USERNAME
                and request.form.get("password") == config.PASSWORD):
            session["user"] = config.USERNAME
            return redirect(url_for("dashboard"))
        error = "Username or password is incorrect."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/data", methods=["POST"])
def receive_data():
    """Called by the ESP32 every few seconds."""
    if request.headers.get("X-API-KEY") != config.DEVICE_KEY:
        return jsonify(error="bad device key"), 403

    data = request.get_json(silent=True) or {}
    try:
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="invalid data"), 400

    latest.update(temperature=temperature, humidity=humidity, time=time.time())
    history.append({
        "time": time.strftime("%H:%M:%S"),
        "temperature": temperature,
        "humidity": humidity,
    })

    new_file = not os.path.exists(config.CSV_FILE)
    with open(config.CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["timestamp", "temperature_c", "humidity_pct"])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), temperature, humidity])

    print(f"Received: {temperature} C, {humidity} %")
    return jsonify(ok=True)


@app.route("/api/latest")
@login_required
def get_latest():
    age = None if latest["time"] is None else round(time.time() - latest["time"])
    return jsonify(
        temperature=latest["temperature"],
        humidity=latest["humidity"],
        age=age,
        history=list(history)[-10:][::-1],
    )


if __name__ == "__main__":
    # host 0.0.0.0 lets the ESP32 and other devices on the same Wi-Fi reach the server
    app.run(host="0.0.0.0", port=5000, debug=False)
