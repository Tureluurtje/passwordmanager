import os
import configparser
import mysql.connector
from core.logup import AuthenticationManager
from core.passwordmanage import PasswordManager

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
            raise ValueError(f"Invalid request method: {requestMethod}")
        
def handleAuthentication(req):
    username = req.args.get("username")
    password = req.args.get("password")
    action = req.args.get("action")

    missing = [name for name, value in [("username", username), ("password", password), ("action")] if not value]
    if missing:
        raise ValueError(f"Missing arguments: {', '.join(missing)}")
    
    authenticationManagerObj = AuthenticationManager(connectToDatabase())
    
    if action == "login":
        return authenticationManagerObj.login(username, password)
    elif action == "register":
        return authenticationManagerObj.register(username, password)
    
def handlePassword(req):
    username = req.args.get("username")
    masterPassword = req.args.get("masterPassword")
    credentialName = req.args.get("credentialName", "")
    credentialUsername = req.args.get("credentialUsername", "")
    credentialPassword = req.args.get("credentialPassword", "")
    action = req.args.get("action")

    missing = [name for name, value in [("username", username), ("master_password", masterPassword), ("action")] if not value]
    if missing:
        raise ValueError(f"Missing arguments: {', '.join(missing)}")

    passwordManagerObj = PasswordManager(connectToDatabase())

    if action == "add":
        return passwordManagerObj.add_password(username, master_password, credentialName, credentialUsername, credentialPassword)
    elif action == "get":
        return passwordManagerObj.get_password(username, master_password, credentialName)
    elif action == "delete":
        return passwordManagerObj.delete_password(username, master_password, credentialName)
    elif action == "update":
        return passwordManagerObj.update_password(username, master_password, credentialName, credentialPassword)
    else:
        raise ValueError(f"Invalid action: {action}")