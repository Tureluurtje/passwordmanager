import hashlib

def fetchSalt(username, dbConnection):
    myCursor = dbConnection.cursor()
    myCursor.execute("SELECT salt FROM users WHERE username = %s", (username,))
    result = myCursor.fetchone()
    myCursor.close()
    
    if result:
        return result[0]
    else:
        return hashlib.sha256(username.encode()).hexdigest()[:32]
