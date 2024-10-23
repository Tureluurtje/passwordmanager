from flask import Flask, jsonify, request
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add the parent directory to the system path


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
    from main import start
    account_owner = request.args.get('account_owner')
    username = request.args.get('username')
    password = request.args.get('password')
    code_totp = request.args.get('code')
    if username and password and code_totp:
        result = start("authenticate", account_owner, username, password, code_totp)
        pattern = r'Too many failed login attempts. Please try again in \d{2}:\d{2}\ '
        if result == 'Logged in':
            return jsonify({"message": "Authentication successful"})
        elif result == 'Wrong credentials':
            return jsonify({"error": "Authentication failed"}), 401
        elif re.match(pattern, result):
            return jsonify({"error": result}), 401
        else:
            return jsonify({"error": "Internal server error"}), 500
    return jsonify({"error": "missing arguments"}), 400
def password():
    from main import start
    
def start_server():
    app.run(debug=True)

if __name__ == '__main__':
    start_server()