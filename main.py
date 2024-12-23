import os
import re
import configparser
import mysql.connector
from flask import Flask, jsonify, request
from core import logup, passwordmanage
from core.returnJson import verifyArgs

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
        return manage_password()
        
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
        result = handle_request("authenticate", account_owner, username, password)
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

def manage_password():
    password_method = request.args.get('password_method')
    username = request.args.get('username')
    password = request.args.get('password')
    account_name = request.args.get('account_name')
    account_username = request.args.get('account_username')
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
        result = handle_request("password", True, username, password, password_method, account_name, account_username, account_password)
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

class Main:
    @staticmethod
    def authenticate_user(account_owner, username, password):
        def login(username, password):
            is_logged_in, master_password, log_attempt = logup.login(username, password)
            if log_attempt:
                if is_logged_in:
                    logup.log(username, 1, "login")
                    return (True, '600', master_password)
                else:
                    logup.log(username, 0, "login")
                    return (False, '700', master_password)
            else:
                return log_attempt

        def register(username, password):
            logup.register(username, password)
            return login(username, password)

        if account_owner:
            return login(username, password)
        else:
            return register(username, password)

    @staticmethod
    def manage_password(method, username, password, account_name='', account_username='', account_password=''):
        is_authenticated, code, master_password = Main.authenticate_user(True, username, password)

        if method == "add":
            if code == "600":
                result = passwordmanage.add_password(username, master_password, account_name, account_username, account_password)
                if result:
                    return (True, '200')
                else:
                    return (False, '500')
            else:
                return (False, '700')
        elif method == "get":
            return passwordmanage.get_password(username, master_password, account_name)
        elif method == "delete":
            return passwordmanage.delete_password(username, master_password, account_name)
        elif method == "update":
            return passwordmanage.update_password(username, master_password, account_name, account_password)
        else:
            return "Invalid method"

def handle_request(method, account_owner, username, password, password_method='', account_name='', account_username='', account_password=''):
    if method == "authenticate":
        args = Main.authenticate_user(account_owner, username, password)
        if isinstance(args, tuple):
            return verifyArgs('http', args)
        return args
    elif method == "password":
        args = Main.manage_password(password_method, username, password, account_name, account_username, account_password)
        translated_args = verifyArgs('http', args[1])
        return args[1]

def connect_to_database():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(root_dir, '..', 'config/config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    mydb = mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['db']
    )
    return mydb

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

