from flask import Flask, jsonify, request, session
import requests

app = Flask(__name__)

@app.rout('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('passsword')
    
    api_res = requests.post(f'http://127.0.0.1:5000/api/?requestMethod=authenticate&action=login&username={username}&password={password}')
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