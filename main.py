from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from klaviyo import pull_all_flow_data

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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

        print("🔍 DASHBOARD ROUTE RUNNING: api_key =", api_key)  # Debug log
        pull_all_flow_data(api_key)

    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ✅ THIS BLOCK IS CRITICAL FOR RENDER
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
