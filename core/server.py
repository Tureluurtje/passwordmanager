import os
import configparser
import mysql.connector

from core.authentication import AuthenticationManager
from core.passwordmanage import PasswordManager
import core.utils

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
        case "utils":
            return handleUtils(req)
        case _:
            return f"Invalid request method: {requestMethod}", 400
        
def handleAuthentication(req):
    action = req.args.get("action")
    if not action:
        return f"Missing arguments: action", 400
    
    dbConnection = connectToDatabase()
    if not dbConnection:
        return "Could not connect to the database", 500
    
    auth = AuthenticationManager(dbConnection)    
    
    if action == "token":
        token = req.args.get("token")
        if not token:
            return "Missing arguments: token", 400
        return AuthenticationManager.verifyAuthToken(token)
    
    required_params = ["username", "password"]    
    missing = [param for param in required_params if not req.args.get(param)]
    
    if missing:
        return f"Missing arguments: {', '.join(missing)}", 400
    
    username = req.args.get("username")
    password = req.args.get("password")
        
    if action == "login":
        return auth.login(username, password)
    elif action == "register":
        return auth.register(username, password)
    else:
        return f"Invalid action: {action}", 400
    
    
def handlePassword(req):
    token = req.args.get("token", "")
    credentialName = req.args.get("credentialName", "")
    credentialUsername = req.args.get("credentialUsername", "")
    credentialPassword = req.args.get("credentialPassword", "")
    action = req.args.get("action")

    missing = [name for name, value in [("token", token), ("action")] if not value]
    if missing:
        return f"Missing arguments: {', '.join(missing)}", 400

    match action:
        case "add":
            return PasswordManager().add_password(token, credentialName, credentialUsername, credentialPassword)
        case "get":
            return PasswordManager().get_password(token, credentialName)
        case "delete":
            return PasswordManager().delete_password(token, credentialName)
        case "update":
            return PasswordManager().update_password(token, credentialName, credentialPassword)
        case _:
            return f"Invalid action: {action}", 400
        
def handleUtils(req):
    action = req.args.get("action", "")

    dbConnection = connectToDatabase()
    if not dbConnection:
        return "Could not connect to the database", 500
    
    try:
        match action:
            case "fetchSalt":
                username = req.args.get("username", "")
                return core.utils.fetchSalt(username, dbConnection), 200
    except:
        return "Internal server error", 500