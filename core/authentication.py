import hashlib
import datetime
import secrets
import time
from mysql.connector import CMySQLConnection
from argon2 import PasswordHasher, exceptions

class AuthenticationManager:
    def __init__(self, conn):
        if isinstance(conn, CMySQLConnection):
            self.conn = conn
        else:
            return "Database connection error", 500

        
    def login(self, username, password) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT password FROM users WHERE username = %s", (username.lower(),))
            result = cur.fetchone()
            cur.close()  # Close cursor
            if not result:
                return "Login failed, username or password is incorrect", 401

            stored_hash = result[0]
            
            ph = PasswordHasher()
            try:
                # Verify password (password is the raw authKey client sends)
                ph.verify(stored_hash, password)
            except exceptions.VerifyMismatchError:
                return "Login failed, username or password is incorrect", 401
        

            token = self.refreshAuthToken(username)
            if token:
                return f"Login successful, {token}", 200
            else:
                raise Exception("Token failed to generate")
        except Exception as e:
            return "There was an error while trying to login", 500  # Return error if there was an error while trying to login
            

    def register(self, username, password) -> bool:
        try:
            cur = self.conn.cursor() # creates cursor object
            cur.execute(f"INSERT INTO users(username, password) VALUES({username}, {password})") # inserts username, password and totp secret into database
            self.conn.commit()  # Commit on the same connection
            cur.close()  # Close cursor
            return "Registration successful", 200  # Return success message
        except:
            return "There was an error while trying to register", 500  # Return error if there was an error while trying to register
    
    def cleanExpiredTokens(self):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM auth_tokens WHERE expires_at < %s", (int(time.time()) + 900,))
            self.conn.commit()
            cur.close()
        except Exception as e:
            return f"Failed to clean expired tokens: {e}", 500

    def refreshAuthToken(self, username, type="access"):
        """
        Generate a new auth token (access or refresh) for a given username.
        - access: default, expires in 5 minutes (sliding)
        - refresh: longer expiry, e.g., 7 days
        First, checks if a valid token exists. If so, returns that.
        """
        try:
            cur = self.conn.cursor()

            # Check for existing valid token
            cur.execute(
                "SELECT token FROM auth_tokens WHERE username = %s AND token_type = %s",
                (username, type)
            )
            existing = cur.fetchone()
            cur.close()

            if existing:
                token = existing[0]
                # Use verifyAuthToken to see if it's still valid
                is_valid, _ = self.verifyAuthToken(token, type=type)
                if is_valid:
                    return token, 200  # Return existing valid token

            # Remove old tokens of this type
            cur = self.conn.cursor()
            cur.execute(
                "DELETE FROM auth_tokens WHERE username = %s AND token_type = %s",
                (username, type)
            )
            self.conn.commit()

            # Generate new token
            token = secrets.token_urlsafe(32)
            if type == "access":
                expiresAt = int(time.time()) + 300  # 5 minutes
            elif type == "refresh":
                expiresAt = int(time.time()) + 7 * 24 * 3600  # 7 days
            else:
                raise ValueError("Invalid token type. Must be 'access' or 'refresh'.")

            # Insert new token
            cur.execute(
                "INSERT INTO auth_tokens(username, token, token_type, expires_at) VALUES(%s, %s, %s, %s)",
                (username, token, type, expiresAt)
            )
            self.conn.commit()
            cur.close()

            return token, 200

        except Exception as e:
            return False, f"Failed to generate {type} token: {e}", 500

    def verifyAuthToken(self, token, type="access"):
        """
        Verify a token (access or refresh).
        Returns (True, username) if valid, else (False, None).
        
        - Access tokens: validity check + sliding expiration (extend 5 minutes).
        - Refresh tokens: validity check only (fixed lifetime).
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT expires_at, username FROM auth_tokens WHERE token = %s AND token_type = %s",
                (token, type)
            )
            result = cur.fetchone()
            cur.close()

            if not result:
                return False, None

            expires_at, username = int(result[0]), result[1]
            now = int(time.time())

            if now < expires_at:
                if type == "access":
                    # Sliding expiration: extend expiry 5 minutes
                    new_expires_at = now + 300
                    cur = self.conn.cursor()
                    cur.execute(
                        "UPDATE auth_tokens SET expires_at = %s WHERE token = %s",
                        (new_expires_at, token)
                    )
                    self.conn.commit()
                    cur.close()

                # Refresh tokens don’t get extended
                return True, username

            return False, None  # token expired

        except Exception:
            return False, None


        
def log(conn, username, verify, logReason) -> None:
    myCursor = conn.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.now(), verify,)) # inserts log of the users action into the database
    conn.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    return
