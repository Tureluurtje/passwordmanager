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
        if account_owner == 'True':
            account_owner = True
        else:
            account_owner = False
    except:
        account_owner = False
    username = request.args.get('username')
    password = request.args.get('password')
    if username and password:
        result = start("authenticate", username, password, account_owner)
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
    password_method = request.args.get('passwordmethod')
    username = request.args.get('username')
    password = request.args.get('password')
    account_name = request.args.get('account_name')
    account_username = request.args.get('account_username')
    account_password = request.args.get('account_password')
    account_notes = request.args.get('account_notes')
    if password_method and username and password:
        pass
    else:
        return jsonify({"error": "missing arguments"}), 400
    if password_method == 'add':
        if account_name and account_password :
            pass
        else:
            return jsonify({"error": "missing arguments"}), 400
        result = start("password", username, password, True, account_name, account_username, account_password, account_notes, password_method)
        if result == 'Wrong credentials': 
            return jsonify({"message": "Password added successfully"}) #TODO fix http codes without http translation straight to here
        elif result == 'Internal server error':
            return jsonify({"error": "Internal server error1"}), 500
        elif result == 'Authentication failed':
            return jsonify({"error": "Authentication failed"}), 401
        else:
            return jsonify({"error": "Internal server error2"}), 500 #BUG alawys 500 while it needs to be 200 addpass
    
def start_server():
    app.run(debug=True)

if __name__ == '__main__':
    start_server()