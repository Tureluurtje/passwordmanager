import os
import configparser
import mysql.connector

from mysql.connector import CMySQLConnection, MySQLConnection

from core.logup import AuthenticationManager
from core.passwordmanage import PasswordManager

def connectToDatabase() -> object:
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
    if not req or not req.args:
        return "Hello World!", 200
    try:
        conn = connectToDatabase()
        if conn is None:
            raise ConnectionError(f"Failed to connect to the database, because the connection is {type(conn).__name__}")
        AuthenticationManager(conn).cleanExpiredTokens()  # Clean expired tokens before login
        conn.close()  # Close the connection if it was successful
    except Exception as e:
        return str(e), 500
    
    requestMethod = req.args.get('requestMethod')

    if not requestMethod:
        return "Missing 'requestMethod' parameter", 400

    match requestMethod:
        case "authenticate":
            return handleAuthentication(req)
        case "password":
            return handlePassword(req)
        case _:
            return f"Invalid request method: {requestMethod}", 400
        
def handleAuthentication(req):
    username = req.args.get("username")
    password = req.args.get("password")
    action = req.args.get("action")

    missing = [name for name, value in [("username", username), ("password", password), ("action", action)] if not value]
    if missing:
        return f"Missing arguments: {', '.join(missing)}", 400
    
    
    dbConnection = connectToDatabase()
    if not dbConnection:
        return "Could not connect to the database", 500
    AuthenticationManagerObj = AuthenticationManager(dbConnection)
    
    match action:
        case "login":
            return AuthenticationManagerObj.login(username, password)
        case "register":
            return AuthenticationManagerObj.register(username, password)
        case _:
            return f"Invalid action: {action}", 400
    
    
def handlePassword(req):
    username = req.args.get("username")
    masterPassword = req.args.get("masterPassword")
    credentialName = req.args.get("credentialName", "")
    credentialUsername = req.args.get("credentialUsername", "")
    credentialPassword = req.args.get("credentialPassword", "")
    action = req.args.get("action")

    missing = [name for name, value in [("username", username), ("master_password", masterPassword), ("action")] if not value]
    if missing:
        return f"Missing arguments: {', '.join(missing)}", 400

    match action:
        case "add":
            return PasswordManager().add_password(username, masterPassword, credentialName, credentialUsername, credentialPassword)
        case "get":
            return PasswordManager().get_password(username, masterPassword, credentialName)
        case "delete":
            return PasswordManager().delete_password(username, masterPassword, credentialName)
        case "update":
            return PasswordManager().update_password(username, masterPassword, credentialName, credentialPassword)
        case _:
            return f"Invalid action: {action}", 400