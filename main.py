from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from klaviyo import pull_all_flow_data

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open("users.json", "r") as f:
            users = json.load(f)

        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        api_key = request.form["api_key"]

        if not username or not password or not api_key:
            return "All fields are required", 400

        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                users = json.load(f)
        else:
            users = {}

        if username in users:
            return "Username already exists", 409

        users[username] = {"password": password, "api_key": api_key}

        with open("users.json", "w") as f:
            json.dump(users, f)

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    with open("users.json", "r") as f:
        users = json.load(f)

    username = session["username"]
    api_key = users.get(username, {}).get("api_key", "")

    if not api_key:
        return "No API key found for this user.", 400

    pull_all_flow_data(api_key)  # ✅ fixed: pass the api_key to the function
    return render_template("dashboard.html", username=username)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
