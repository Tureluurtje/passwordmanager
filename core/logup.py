import hashlib
import datetime
import secrets
import time

class AuthenticationManager:
    def __init__(self, connectToDatabase=None):
        if connectToDatabase is None:
            raise ValueError("connectToDatabase is required")
        self.connectToDatabase = connectToDatabase
        
    def login(self, username, password) -> bool:
        hasAuthToken = AuthenticationManager(self.connectToDatabase).verifyAuthToken(username)
        if hasAuthToken:
            return True
        else:
            conn = self.connectToDatabase()  # Get a new connectionwith self.connectToDatabase() as conn:
            myCursor = conn.cursor()
            myCursor.execute("SELECT COUNT(*) FROM users WHERE username = %s AND password = %s", (username.lower(), password))  # Check if the username exists in the database
            result = myCursor.fetchone()
            myCursor.close()  # Close cursor
            if result:  # Check if match found
                if AuthenticationManager(self.connectToDatabase).generateAuthToken(username):  # Generate auth token if username exists
                    return True
            return False

    def register(self, username, password) -> bool:
        try:
            conn = self.connectToDatabase()  # Get a new connection
            myCursor = conn.cursor() # creates cursor object
            myCursor.execute(f"INSERT INTO users(username, password) VALUES('{username}', '{hashlib.sha256(password.encode()).hexdigest()}')") # inserts username, password and totp secret into database
            conn.commit()  # Commit on the same connection
            myCursor.close()  # Close cursor
            return True
        except:
            return False
        
    def generateAuthToken(self, username) -> bool:
        token = secrets.token_urlsafe(32) # Generate a random token
        expiresAt = int(time.time()) + 300 # Token expires in 5 minutes
        try:
            conn = self.connectToDatabase()  # Get a new connection
            myCursor = conn.cursor() # creates cursor object
            myCursor.execute(
                "INSERT INTO auth_tokens(username, token, expires_at) VALUES(%s, %s, %s)"
                "ON CONFLICT (username) DO UPDATE SET token = EXCLUDED.token, expires_at = EXCLUDED.expires_at",
                (username, token, expiresAt)) # inserts token into database
            conn.commit()  # Commit on the same connection
            myCursor.close()  # Close cursor
            return True
        except Exception:
            return False
        
    def verifyAuthToken(self, username) -> bool:
        conn = self.connectToDatabase()  # Get a new connection
        myCursor = conn.cursor()
        myCursor.execute("SELECT token, expires_at FROM auth_tokens WHERE username = %s", (username,))
        result = myCursor.fetchone()
        myCursor.close()
        if result:
            username, expires_at = result
            if int(time.time()) < expires_at:
                return True
        return False
        
def log(conn, username, verify, logReason) -> None:
    myCursor = conn.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.datetime.now(), verify,)) # inserts log of the users action into the database
    conn.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    return
