from core.logup import AuthenticationManager
from core.passwordmanage import PasswordManager

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
    
    if action == "login":
        return AuthenticationManager.login(username, password)
    elif action == "register":
        return AuthenticationManager.register(username, password)
    
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