from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
import sqlite3
import os

app = Flask(__name__)

# =========================
# DATABASE
# =========================

DATABASE = "users.db"


def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Datenbank beim Start erstellen
init_db()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# REDSTONE
# =========================

@app.route("/redstone")
def redstone():
    return render_template("redstone.html")


# =========================
# BUILDINGS
# =========================

@app.route("/buildings")
def buildings():
    return render_template("buildings.html")


# =========================
# FARMS
# =========================

@app.route("/farms")
def farms():
    return render_template("farms.html")


# =========================
# SIGN UP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Wenn die Seite nur geöffnet wird
    if request.method == "GET":
        return render_template("signup.html")

    # Daten aus dem Formular holen
    username = request.form.get("username")
    password = request.form.get("password")

    # Prüfen, ob beide Felder ausgefüllt sind
    if not username or not password:
        return "Bitte Username und Passwort eingeben."

    # Passwort sicher verschlüsseln / hashen
    password_hash = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DATABASE)

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password_hash)
        )

        conn.commit()
        conn.close()

        return """
        <h1>Account erstellt! ✅</h1>
        <p>Dein Account wurde erfolgreich gespeichert.</p>
        <a href="/">Zur Startseite</a>
        """

    except sqlite3.IntegrityError:
        return """
        <h1>Username bereits vergeben ❌</h1>
        <p>Dieser Username existiert bereits.</p>
        <a href="/signup">Zurück</a>
        """


# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    app.run(debug=True)
