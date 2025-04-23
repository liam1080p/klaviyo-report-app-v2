from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from klaviyo import pull_all_flow_data

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with something secure!

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with open('users.json') as f:
            users = json.load(f)
        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with open('users.json') as f:
            users = json.load(f)
        if email in users:
            return 'User already exists'
        users[email] = password
        with open('users.json', 'w') as f:
            json.dump(users, f)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        api_key = request.form['api_key']
        pull_all_flow_data(api_key)
        return '✅ CSV generated successfully!'

    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
