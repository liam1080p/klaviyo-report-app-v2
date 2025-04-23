from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from klaviyo import pull_all_flow_data  # Make sure this file is in your project

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a secure key in production

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        api_key = request.form['api_key']

        users = load_users()
        if username in users:
            return "Username already exists. Please choose another."

        users[username] = {
            'password': password,
            'api_key': api_key
        }
        save_users(users)
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))

        return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    users = load_users()
    user_data = users.get(session['user'])

    if user_data:
        api_key = user_data.get('api_key')
        if not api_key:
            return "No API key found for user", 400

        pull_all_flow_data(api_key)  # ✅ FIXED: now includes the API key

    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
