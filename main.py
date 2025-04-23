from flask import Flask, render_template, request, redirect, session, url_for
import json, os
from klaviyo import pull_all_flow_data

app = Flask(__name__)
app.secret_key = os.urandom(24)  # ✅ Fix: needed for sessions to work properly

USERS_FILE = 'users.json'

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
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users:
            return 'User already exists'
        users[email] = {'password': password}
        save_users(users)
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users and users[email]['password'] == password:
            session['user'] = email
            return redirect('/dashboard')
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    pull_all_flow_data()  # this pulls and writes flow_metrics.csv
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
