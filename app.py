from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/redstone")
def redstone():
    return render_template("redstone.html")


@app.route("/building")
def building():
    return render_template("building.html")


@app.route("/farms")
def farms():
    return render_template("farms.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True)