import hashlib
import datetime
import secrets
import time
from mysql.connector import CMySQLConnection, MySQLConnection

class AuthenticationManager:
    def __init__(self, dbConnection):
        if dbConnection is not CMySQLConnection or dbConnection is not MySQLConnection:
            raise ValueError("dbConnection is not valid")
        self.dbConnection = dbConnection

        
    def login(self, username, password) -> bool:
        hasAuthToken = self.verifyAuthToken(username)
        if hasAuthToken:
            return True
        else:
            myCursor = self.dbConnection.cursor()
            myCursor.execute("SELECT COUNT(*) FROM users WHERE username = %s AND password = %s", (username.lower(), password))  # Check if the username exists in the database
            result = myCursor.fetchone()
            myCursor.close()  # Close cursor
            if result:  # Check if match found
                if self.generateAuthToken(username):  # Generate auth token if username exists
                    return True
            return False

    def register(self, username, password) -> bool:
        try:
            myCursor = self.dbConnection.cursor() # creates cursor object
            myCursor.execute(f"INSERT INTO users(username, password) VALUES('{username}', '{hashlib.sha256(password.encode()).hexdigest()}')") # inserts username, password and totp secret into database
            self.dbConnection.commit()  # Commit on the same connection
            myCursor.close()  # Close cursor
            return True
        except:
            return False
        
    def generateAuthToken(self, username) -> bool:
        token = secrets.token_urlsafe(32) # Generate a random token
        expiresAt = int(time.time()) + 300 # Token expires in 5 minutes
        try:
            myCursor = self.dbConnection.cursor() # creates cursor object
            myCursor.execute(
                "INSERT INTO auth_tokens(username, token, expires_at) VALUES(%s, %s, %s)",
                (username, token, expiresAt)) # inserts token into database
            self.dbConnection.commit()  # Commit on the same connection
            myCursor.close()  # Close cursor
            return True
        except Exception as e:
            return False
        
    def verifyAuthToken(self, username) -> bool:
        myCursor = self.dbConnection.cursor()
        myCursor.execute("SELECT token, expires_at FROM auth_tokens WHERE username = %s", (username,))
        result = myCursor.fetchone()
        myCursor.close()
        if result:
            username, expires_at = result
            if int(time.time()) < expires_at:
                return True
        return False
        
def log(dbConnection, username, verify, logReason) -> None:
    myCursor = dbConnection.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.datetime.now(), verify,)) # inserts log of the users action into the database
    dbConnection.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    return
