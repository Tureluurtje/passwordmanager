import os
import configparser
import mysql.connector

from mysql.connector.connection_cext import CMySQLConnection

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
    except mysql.connector.Error:
        return None

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
    except mysql.connector.Error:
        return None

def requestHandler(req):
    try:
        conn = connectToDatabase()
        if conn == CMySQLConnection:
            raise ConnectionError("Failed to connect to the database")
        conn.close()  # Close the connection if it was successful
    except Exception as e:
        return {"error": str(e)}, 500
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

    missing = [name for name, value in [("username", username), ("password", password), ("action", action)] if not value]
    if missing:
        raise ValueError(f"Missing arguments: {', '.join(missing)}")
    
    
    dbConnection = connectToDatabase()
    if not dbConnection:
        raise ValueError("Could not connect to the database")
    AuthenticationManagerObj = AuthenticationManager(dbConnection)
    
    if action == "login":
        return AuthenticationManagerObj.login(username, password)
    elif action == "register":
        return AuthenticationManagerObj.register(username, password)
    
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

    if action == "add":
        return PasswordManager().add_password(username, masterPassword, credentialName, credentialUsername, credentialPassword)
    elif action == "get":
        return PasswordManager().get_password(username, masterPassword, credentialName)
    elif action == "delete":
        return PasswordManager().delete_password(username, masterPassword, credentialName)
    elif action == "update":
        return PasswordManager().update_password(username, masterPassword, credentialName, credentialPassword)
    else:
        raise ValueError(f"Invalid action: {action}")