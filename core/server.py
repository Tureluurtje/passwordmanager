import os
import configparser
import mysql.connector
from logup import AuthenticationManager
from passwordmanage import PasswordManager

def connectToDatabase():
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(root_dir, '..', 'config/config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        mydb = mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['db']
        ) # creates connection to database using a config file
        return mydb 
    except mysql.connector.Error as e:
        return e

def requestHandler(req):
    requestMethod = req.args.get('requestMethod')

    if not requestMethod:
        raise ValueError("Missing 'requestMethod' parameter")

    match requestMethod:
        case "authenticate":
            return handleAuthentication(req)
        case "password":
            return handlePassword(req)
        case _:
            raise ValueError(f"Invalid request method: {"requestMethod"}")
        
def handleAuthentication(req):
    username = req.args.get("username")
    password = req.args.get("password")
    action = req.args.get("action")

    missing = [name for name, value in [("username", username), ("password", password), ("action")] if not value]
    if missing:
        raise ValueError(f"Missing arguments: {', '.join(missing)}")
    
    if action == "login":
        return AuthenticationManager.login(username, password)
    elif action == "register":
        return AuthenticationManager.register(username, password)
    
def handlePassword(req):
    username = req.args.get("username")
    master_password = req.args.get("master_password")
    credentialName = req.args.get("account_name", "")
    credentialUsername = req.args.get("account_username", "")
    credentialPassword = req.args.get("account_password", "")
    action = req.args.get("action")

    missing = [name for name, value in [("username", username), ("master_password", master_password), ("action")] if not value]
    if missing:
        raise ValueError(f"Missing arguments: {', '.join(missing)}")

    password_manager = PasswordManager()

    if action == "add":
        return password_manager.add_password(username, master_password, credentialName, credentialUsername, credentialPassword)
    elif action == "get":
        return password_manager.get_password(username, master_password, credentialName)
    elif action == "delete":
        return password_manager.delete_password(username, master_password, credentialName)
    elif action == "update":
        return password_manager.update_password(username, master_password, credentialName, credentialPassword)
    else:
        raise ValueError(f"Invalid action: {action}")