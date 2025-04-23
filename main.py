from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from klaviyo import pull_all_flow_data

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

USERS_FILE = 'users.json'

# Helper functions to manage users
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login", 400
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        email = request.form['email']
        password = request.form['password']
        api_key = request.form['api_key']
        if email in users:
            return "User already exists", 400
        users[email] = {'password': password, 'api_key': api_key}
        save_users(users)
        session['user'] = email
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

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
        pull_all_flow_data(api_key)  # ✅ fixed — pass api_key here
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=10000)
