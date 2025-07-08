from flask import Flask, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='web', static_url_path='/')
app.secret_key = '#611OaA1!'

# @CRITICAL: Change app.config.update before production
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE='Lax'
)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to /login
    return f"Welcome, {session['username']}!"

@app.route('/login', methods=['GET'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    return app.send_static_file('login.html')  # Serve the login page

# Note: The following endpoints are POST requests to handle login and logout actions.
@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    api_res = requests.get(f'http://127.0.0.1:5000/?requestMethod=authenticate&action=login&username={username}&password={password}')
    if api_res.ok:
        session['username'] = username
        session['logged_in'] = True
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=4000)  # Run the Flask app on localhost:5000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.
# This is a simple Flask application that serves as an API for password management.