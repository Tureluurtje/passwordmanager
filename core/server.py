import os
import configparser
import mysql.connector
from flask import jsonify

from core.authentication import AuthenticationManager
from core.passwordmanage import PasswordManager
import core.utils as utils

def connectToDatabase() -> mysql.connector.connection_cext.CMySQLConnection:
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(root_dir, "..", "config/config.ini")
        config = configparser.ConfigParser()
        config.read(config_path)
        conn = mysql.connector.connect(
            host=config["database"]["host"],
            user=config["database"]["user"],
            password=config["database"]["password"],
            database=config["database"]["db"]
        ) # creates connection to database using a config file
        return conn 
    except mysql.connector.Error:
        return None
        
def handleAuth(subpath: str, data: dict, auth_token: str=None) -> dict:    
    conn = connectToDatabase()
    if not conn:
        return "Could not connect to the database", 500
    
    auth = AuthenticationManager(conn)    
    try:
        auth.cleanExpiredTokens()
        if auth_token and subpath not in ["refresh", "access"]:
            is_valid, username = auth.verifyAuthToken(auth_token)
            if not is_valid:
                return jsonify({"success": False, "error": "Invalid or expired token"}), 401
    except Exception as e:
        return str(e), 500
    
    if subpath == "login":
        username = data.get("username")
        password = data.get("password")
        return auth.login(username, password)
    elif subpath == "register":
        password = data.get("password")
        return auth.register(username, password)
    elif subpath == "access":
        return auth.refreshAuthToken(auth_token)
    elif subpath == "refresh":
        username = data.get("username")
        return auth.refreshAuthToken(username, "access")
    elif subpath == "salt":
        username = data.get("username")
        return utils.fetchSalt(conn, username)
     
def handlePassword(data: dict) -> dict:
    token = data.get("token", "")
    username = data.get("username", "")
    action = data.get("action")

    missing = [name for name, value in [("token", token), ("action", action)] if not value]
    if missing:
        return f"Missing arguments: {", ".join(missing)}", 400

    conn = connectToDatabase()
    if not conn:
        return "Could not connect to the database", 500

    password = PasswordManager(conn)

    try:
        authenticated = AuthenticationManager(conn).verifyAuthToken(token)
        if not authenticated:
            return "Invalid token", 401
    except Exception as e:
        return f"Authentication error: {str(e)}", 500
    finally:
        conn.close()
        
    
    if action == "add":
        payload = data.get("payload", {})
        return password.add_password(username, payload)
    elif action == "get":
        return password.get_password(username)
    elif action == "update":
        passwordId = data.get("passwordId", "")
        replacements = data.get("replacements", "")
        return password.update_password(username, passwordId, replacements)
    elif action == "delete":
        passwordId = data.get("passwordId", "")
        return password.delete_password(username, passwordId)
    else:
        return f"Invalid action: {action}", 400
        
def handleUtils(data: dict) -> dict:
    action = data.get("action", "")

    conn = connectToDatabase()
    if not conn:
        return "Could not connect to the database", 500
    
    try:
        match action:
            case "fetchSalt":
                username = data.get("username", "")
                return utils.fetchSalt(username, conn), 200
            case "setBreached":
                username = data.get("username", "")
                passwordId = data.get("passwordId", "")
                value = data.get("value", "")
                return utils.setBreached(username, passwordId, value, conn), 200
    except:
        return "Internal server error", 500
    finally:
        conn.close()