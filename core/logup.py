import hashlib
import datetime
import secrets
import time

from core.connection import connectToDatabase


class AuthenticationManager:
    def __init__(self):
        pass
    
    @staticmethod
    def login(username, password) -> bool:
        hasAuthToken = AuthenticationManager.verifyAuthToken(username)
        if hasAuthToken:
            return True
        else:
            conn = connectToDatabase()
            myCursor = conn.cursor()  # creates cursor object
            myCursor.execute(f"SELECT password FROM users WHERE username = '{username}'")
            result = myCursor.fetchone()  # fetches the first row of the result
            myCursor.close()
            conn.close()  # Close connection
            if result == password:  # checks if the password matches
                AuthenticationManager.generateAuthToken(username)  # generates a new auth token
                return True
        return False
    
    @staticmethod
    def register(username, password) -> bool:
        try:
            conn = connectToDatabase()
            myCursor = conn.cursor() # creates cursor object
            myCursor.execute(f"INSERT INTO users(username, password) VALUES('{username}', '{hashlib.sha256(password.encode()).hexdigest()}')") # inserts username, password and totp secret into database
            conn.commit()  # Commit on the same connection
            myCursor.close()  # Close cursor
            conn.close()  # Close connection
            
            return True
        except:
            return False
    @staticmethod
    def generateAuthToken(username) -> str:
        token = secrets.token_urlsafe(32)
        expiresAt = int(time.time()) + 300  # Store as integer timestamp
        try:
            conn = connectToDatabase()
            myCursor = conn.cursor()
            # Insert or update the token for the user
            myCursor.execute(
                "INSERT INTO auth_tokens (username, token, expires_at) VALUES (%s, %s, %s) "
                "ON CONFLICT (username) DO UPDATE SET token = EXCLUDED.token, expires_at = EXCLUDED.expires_at",
                (username, token, expiresAt)
            )
            conn.commit()
            myCursor.close()
            conn.close()
            return token
        except Exception as e:
            # Handle/log exception as needed
            return e
    
    @staticmethod
    def verifyAuthToken(token) -> bool:
        conn = connectToDatabase()
        myCursor = conn.cursor()
        myCursor.execute(f"SELECT username, expires_at FROM auth_tokens WHERE token = {token}")
        result = myCursor.fetchone()
        myCursor.close()
        conn.close()
        if result:
            username, expires_at = result
            if int(time.time()) < expires_at:
                return True
        return False
    
def log(username, verify, logReason) -> None:
    conn = connectToDatabase()
    myCursor = conn.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.datetime.now(), verify,)) # inserts log of the users action into the database
    conn.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    conn.close()  # Close connection
    return
