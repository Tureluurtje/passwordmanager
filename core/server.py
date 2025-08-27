import os
import configparser
import mysql.connector

from core.authentication import AuthenticationManager
from core.passwordmanage import PasswordManager
import core.utils as utils

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
    data = req.get_json(silent=True) or {} #Parse json data
    
    requestMethod = data.get('requestMethod')

    if not requestMethod:
        return "Missing 'requestMethod' parameter", 400

    match requestMethod:
        case "authenticate":
            return handleAuthentication(data)
        case "password":
            return handlePassword(data)
        case "utils":
            return handleUtils(data)
        case _:
            return f"Invalid request method: {requestMethod}", 400
        
def handleAuthentication(data):
    action = data.get("action")

    if not action:
        return f"Missing arguments: action", 400
        
    
    dbConnection = connectToDatabase()
    if not dbConnection:
        return "Could not connect to the database", 500
    
    
    auth = AuthenticationManager(dbConnection)    
    try:
        auth.cleanExpiredTokens()
    except Exception as e:
        return str(e), 500
    
    if action == "token":
        token = data.get("token")
        if not token:
            return "Missing arguments: token", 400
        return AuthenticationManager.verifyAuthToken(token)
    
    required_params = ["username", "password"]    
    missing = [param for param in required_params if not data.get(param)]
    
    if missing:
        return f"Missing arguments: {', '.join(missing)}", 400
    
    username = data.get("username")
    password = data.get("password")
        
    if action == "login":
        return auth.login(username, password)
    elif action == "register":
        return auth.register(username, password)
    else:
        return f"Invalid action: {action}", 400
    
    
def handlePassword(data):
    token = data.get("token", "")
    username = data.get("username", "")
    action = data.get("action")

    missing = [name for name, value in [("token", token), ("action", action)] if not value]
    if missing:
        return f"Missing arguments: {', '.join(missing)}", 400

    dbConnection = connectToDatabase()
    if not dbConnection:
        return "Could not connect to the database", 500

    password = PasswordManager(dbConnection)

    try:
        authenticateDbConnection = connectToDatabase()
        authenticated = AuthenticationManager(authenticateDbConnection).verifyAuthToken(token)
        authenticateDbConnection.close()
        if not authenticated:
            return "Invalid token", 401
    except Exception as e:
        return f"Authentication error: {str(e)}", 500
    
    if action == "add":
        payload = data.get("payload", {})
        return password.add_password(username, payload)
    elif action == "get":
        return password.get_password(username)
    elif action == "delete":
        pass
        #return password.delete_password(token, credentialName)
    elif action == "update":
        pass
        #return password.update_password(token, credentialName, credentialPassword)
    else:
        return f"Invalid action: {action}", 400
        
def handleUtils(data):
    action = data.get("action", "")

    dbConnection = connectToDatabase()
    if not dbConnection:
        return "Could not connect to the database", 500
    
    try:
        match action:
            case "fetchSalt":
                username = data.get("username", "")
                return utils.fetchSalt(username, dbConnection), 200
            case "setBreached":
                username = data.get("username", "")
                passwordId = data.get("passwordId", "")
                value = data.get("value", "")
                return utils.setBreached(username, passwordId, value, dbConnection), 200
    except:
        return "Internal server error", 500