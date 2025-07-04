import hashlib
import datetime
import secrets
import time
from datetime import datetime, date, timezone
from mysql.connector import CMySQLConnection, MySQLConnection

class AuthenticationManager:
    def __init__(self, dbConnection):
        if isinstance(dbConnection, (CMySQLConnection, MySQLConnection)):
            self.dbConnection = dbConnection
        else:
            raise ValueError("dbConnection is not valid")

        
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
        
    def verifyAuthToken(self, token) -> bool:
        myCursor = self.dbConnection.cursor()
        myCursor.execute("SELECT expires_at FROM auth_tokens WHERE token = %s", (token,))
        result = myCursor.fetchone()
        myCursor.close()

        if result:
            expires_at = result[0]
            if isinstance(expires_at, date) and not isinstance(expires_at, datetime):
                expires_at = datetime.combine(expires_at, datetime.min.time())
            if isinstance(expires_at, datetime):
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                expires_at_ts = expires_at.timestamp()

                if time.time() < expires_at_ts:
                    return True

        return False
        
def log(dbConnection, username, verify, logReason) -> None:
    myCursor = dbConnection.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.now(), verify,)) # inserts log of the users action into the database
    dbConnection.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    return
