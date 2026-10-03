from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid

app = Flask(__name__)

app.secret_key = "mctutorials-secret-key"

DATABASE = "users.db"

UPLOAD_FOLDER = "static/profile_pictures"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================
# DATABASE
# =========================

def init_db():

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            profile_picture TEXT DEFAULT 'default.png'
        )
    """)

    conn.commit()
    conn.close()


def add_profile_picture_column():

    conn = sqlite3.connect(DATABASE)

    try:

        conn.execute(
            "ALTER TABLE users ADD COLUMN profile_picture TEXT DEFAULT 'default.png'"
        )

        conn.commit()

    except sqlite3.OperationalError:

        pass

    conn.close()


init_db()
add_profile_picture_column()


# =========================
# UPLOAD
# =========================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


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

    if request.method == "GET":

        return render_template("signup.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:

        return "Bitte Username und Passwort eingeben."

    password_hash = generate_password_hash(password)

    try:

        conn = sqlite3.connect(DATABASE)

        conn.execute(
            """
            INSERT INTO users
            (username, password, profile_picture)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, "default.png")
        )

        conn.commit()
        conn.close()

        session["username"] = username

        return redirect(url_for("home"))

    except sqlite3.IntegrityError:

        return """
        <h1>Username bereits vergeben ❌</h1>

        <p>Dieser Username existiert bereits.</p>

        <a href="/signup">
            Zurück zu Sign Up
        </a>
        """


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect(DATABASE)

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    conn.close()

    if user and check_password_hash(user[2], password):

        session["username"] = username

        return redirect(url_for("home"))

    return """
    <h1>Login fehlgeschlagen ❌</h1>

    <p>Username oder Passwort ist falsch.</p>

    <a href="/login">
        Zurück zum Login
    </a>
    """


# =========================
# PROFILE
# =========================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "username" not in session:

        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":

        if "profile_picture" not in request.files:

            return "Kein Bild ausgewählt."

        file = request.files["profile_picture"]

        if file.filename == "":

            return "Kein Bild ausgewählt."

        if not allowed_file(file.filename):

            return "Nur PNG, JPG, JPEG und WEBP sind erlaubt."

        extension = file.filename.rsplit(".", 1)[1].lower()

        filename = str(uuid.uuid4()) + "." + extension

        os.makedirs(
            app.config["UPLOAD_FOLDER"],
            exist_ok=True
        )

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        conn = sqlite3.connect(DATABASE)

        conn.execute(
            """
            UPDATE users
            SET profile_picture = ?
            WHERE username = ?
            """,
            (filename, username)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("profile"))

    conn = sqlite3.connect(DATABASE)

    user = conn.execute(
        """
        SELECT profile_picture
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    profile_picture = (
        user[0]
        if user and user[0]
        else "default.png"
    )

    return render_template(
        "profile.html",
        profile_picture=profile_picture
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("username", None)

    return redirect(url_for("home"))


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(debug=True)
