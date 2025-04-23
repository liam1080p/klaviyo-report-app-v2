from flask import Flask, render_template, request, redirect, session, url_for, send_file
import json
import os
import csv
from klaviyo import pull_all_flow_data  # Your working script goes here

app = Flask(__name__)
app.secret_key = 'super_secret_key'

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users:
            return "User already exists!"
        users[email] = {"password": password}
        save_users(users)
        session['user'] = email
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users and users[email]['password'] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('csv_ready', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template(
        'dashboard.html',
        user=session['user'],
        csv_ready=session.get('csv_ready', False)
    )

@app.route('/generate-csv', methods=['POST'])
def generate_csv():
    if 'user' not in session:
        return redirect(url_for('login'))

    api_key = request.form['api_key']
    try:
        data = pull_all_flow_data(api_key)

        # Save to CSV
        with open('flow_metrics.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        session['csv_ready'] = True
    except Exception as e:
        return f"❌ Error: {e}"

    return redirect(url_for('dashboard'))

@app.route('/download-csv')
def download_csv():
    if 'csv_ready' in session and session['csv_ready']:
        return send_file("flow_metrics.csv", as_attachment=True)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
