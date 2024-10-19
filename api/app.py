from flask import Flask, jsonify, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add the parent directory to the system path
from main import startAuthenticate
import re

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Hello, World!'})

@app.route('/api/data', methods=['GET'])
def handle_data():
    method = request.args.get('method')
    
    if method == 'authenticate':
        return authenticate()
    
    return jsonify({"error": "Invalid method"}), 400


def authenticate():
    account_owner = request.args.get('account_owner')
    username = request.args.get('username')
    password = request.args.get('password')
    code_totp = request.args.get('code')
    if username and password and code_totp:
        result = startAuthenticate(account_owner, username, password, code_totp)
        pattern = r'Too many failed login attempts. Please try again in \d{2}:\d{2}\.'
        if result == 'logged in':
            return jsonify({"message": "Authentication successful"})
        elif result == 'wrong username, authentication code or password':
            return jsonify({"error": "Authentication failed"}), 401
        elif re.match(pattern, result):
            return jsonify({"error": result}), 401
        else:
            return jsonify({"error": "Internal server error"}), 500
            
    return jsonify({"error": "missing arguments"}), 400

if __name__ == '__main__':
    app.run(debug=True)