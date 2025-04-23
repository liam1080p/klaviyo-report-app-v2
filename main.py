from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from klaviyo import pull_all_flow_data  # Assumes this script already works

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return "Invalid login", 401
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        api_key = request.form['api_key']
        users[username] = {'password': password, 'api_key': api_key}
        save_users(users)
        return redirect('/login')
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    users = load_users()
    user = users.get(username)

    if user:
        api_key = user.get('api_key')
        if api_key:
            pull_all_flow_data(api_key)  # Your existing function
            return render_template('dashboard.html', message="CSV generated")
    
    return render_template('dashboard.html', message="Something went wrong")

# ✅ THIS is the key for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
