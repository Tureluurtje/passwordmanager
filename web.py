from flask import Flask, jsonify, request, session, redirect, url_for, render_template, make_response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import requests

import config.config as config

app = Flask(__name__, static_folder='web', static_url_path='/', template_folder='web')
app.secret_key = config.SECRET_KEY  # @CRITICAL: Change this to a secure key in production

# @CRITICAL: Change app.config.update before production
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE='Lax'
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to /login
    return render_template('index.html', username=session.get('username'), token = session.get('auth_token'))

@app.route('/login', methods=['GET'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('login.html')  # Serve the login page

# Note: The following endpoints are POST requests to handle login and logout actions.
@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    method = data.get('method')

    
    match method:
        case 'authenticate':
            username = data.get('username')
            password = data.get('password')
            try:
                api_res = requests.post(
                    f'{config.HOST}:{config.PORT_API}/',
                    json={
                        "requestMethod": "authenticate",
                        "action": "login",
                        "username": username,
                        "password": password
                    }
                )

                if api_res.ok:
                    session['username'] = username
                    session['logged_in'] = True
                    message = api_res.json().get('message', '')
                    token = message.split(", ('")[1].split("'")[0]  # You might want to improve this parsing later
                    session['auth_token'] = token  # Store token securely in session (Flask will handle the cookie)
                    return jsonify({'success': True}), 200
                else:
                    return jsonify({'success': False}), 401
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        case 'salt':
            username = data.get('username')
            try:
                api_res = requests.post(
                    f'{config.HOST}:{config.PORT_API}/',
                    json={
                        "requestMethod": "utils",
                        "action": "fetchSalt",
                        "username": username
                    }
                )

                if api_res.ok:
                    return jsonify({'success': True, 'salt': api_res.json()}), 200
                else:
                    return jsonify({'success': False}), 500
            except Exception as e:
                return jsonify({'succes': False, 'error': str(e)}), 500

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.FLASK_HOST, port=config.PORT_WEB)  # Run the Flask app on passafe.local:4000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.
# This is a simple Flask application that serves as an API for password management.