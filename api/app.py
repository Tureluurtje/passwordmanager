from flask import Flask, jsonify, request
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add the parent directory to the system path
from main import start

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Hello, World!'})
@app.route('/ping/')
def ping():
    return jsonify('pong')
@app.route('/api/', methods=['GET'])
def handle_data():
    method = request.args.get('method')
    
    if method == 'authenticate':
        return authenticate()
    elif method == 'password':
        return password()
        
    return jsonify({"error": "Invalid method"}), 400

def authenticate():
    try:
        account_owner = request.args.get('account_owner')
        if account_owner:
            account_owner = True
    except:
        account_owner = False
    username = request.args.get('username')
    password = request.args.get('password')
    if username and password:
        result = start("authenticate", account_owner, username, password)
        pattern = r'Too many failed login attempts. Please try again in \d{2}:\d{2}\ '
        if result == 'Logged in':
            return jsonify({"message": "Authentication successful"}), 200
        elif result == 'Wrong credentials':
            return jsonify({"error": "Authentication failed"}), 401
        elif re.match(pattern, result):
            return jsonify({"error": result}), 401
        else:
            return jsonify({"error": "Internal server error"}), 500
    return jsonify({"error": "missing arguments"}), 400

def password():
    password_method = request.args.get('passwordmethod')
    username = request.args.get('username')
    password = request.args.get('password')
    account_name = request.args.get('account_name')
    account_password = request.args.get('account_password')
    if password_method and username and password:
        pass
    else:
        return jsonify({"error": "missing arguments"}), 400
    if password_method == 'add':
        if account_name and account_password:
            pass
        else:
            return jsonify({"error": "missing arguments"}), 400
        result = start("password", password_method, username, password, account_name, account_password)
        if result == '200':
            return jsonify({"message": "Password added successfully"}), 200
        elif result == '500':
            return jsonify({"error": "Internal server error"}), 500
        elif result == '700':
            return jsonify({"error": "Authentication failed"}), 401
        else:
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({"error": "Invalid password method"}), 400

def start_server():
    app.run(debug=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
