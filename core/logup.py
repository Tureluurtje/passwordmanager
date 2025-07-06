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
            return "Databse connection error", 500

        
    def login(self, username, password) -> bool:
        try:
            myCursor = self.dbConnection.cursor()
            myCursor.execute("SELECT COUNT(*) FROM users WHERE username = %s AND password = %s", (username.lower(), password))  # Check if the username and password combo exists in the database
            result = myCursor.fetchone()
            myCursor.close()  # Close cursor
            if result and result[0] > 0 and self.generateAuthToken(username):  # Check if match found
                    return "Login successful", 200
            return "Login failed, username or password is incorrect", 401  # Return error if no match found
        except:
            return "There was an error while trying to login", 500  # Return error if there was an error while trying to login
            

    def register(self, username, password) -> bool:
        try:
            myCursor = self.dbConnection.cursor() # creates cursor object
            myCursor.execute(f"INSERT INTO users(username, password) VALUES('{username}', '{password}')") # inserts username, password and totp secret into database
            self.dbConnection.commit()  # Commit on the same connection
            myCursor.close()  # Close cursor
            return "Registration successful", 200  # Return success message
        except:
            return "There was an error while trying to register", 500  # Return error if there was an error while trying to register
    
    def cleanExpiredTokens(self):
        try:
            myCursor = self.dbConnection.cursor()
            myCursor.execute("DELETE FROM auth_tokens WHERE expires_at < %s", (int(time.time()) + 300,))
            self.dbConnection.commit()
            myCursor.close()
        except Exception as e:
            return f"Failed to clean expired tokens: {e}", 500

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
                # Update expires_at to current time + 5 minutes
                new_expires_at = int(time.time()) + 300
                update_cursor = self.dbConnection.cursor()
                update_cursor.execute(
                    "UPDATE auth_tokens SET expires_at = %s WHERE token = %s",
                    (new_expires_at, token)
                )
                self.dbConnection.commit()
                update_cursor.close()
                return True
        return False
        
def log(dbConnection, username, verify, logReason) -> None:
    myCursor = dbConnection.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.now(), verify,)) # inserts log of the users action into the database
    dbConnection.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    return
