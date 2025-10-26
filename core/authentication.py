import hashlib
import datetime
import secrets
import time
from datetime import datetime, date, timezone
from mysql.connector import CMySQLConnection, MySQLConnection
from argon2 import PasswordHasher, exceptions

class AuthenticationManager:
    def __init__(self, dbConnection):
        if isinstance(dbConnection, (CMySQLConnection, MySQLConnection)):
            self.dbConnection = dbConnection
        else:
            return "Database connection error", 500


    def login(self, username, password) -> bool:
        try:
            myCursor = self.dbConnection.cursor()
            myCursor.execute("SELECT password FROM users WHERE username = %s", (username.lower(),))
            result = myCursor.fetchone()
            myCursor.close()  # Close cursor
            if not result:
                return "Login failed, username or password is incorrect", 401

            stored_hash = result[0]

            ph = PasswordHasher()
            try:
                # Verify password (password is the raw authKey client sends)
                ph.verify(stored_hash, password)
            except exceptions.VerifyMismatchError:
                return "Login failed, username or password is incorrect", 401


            token = self.generateAuthToken(username)
            if token:
                return f"Login successful, {token}", 200
            else:
                raise Exception("Token failed to generate")
        except Exception as e:
            return "There was an error while trying to login", 500  # Return error if there was an error while trying to login


    def register(self, username, password) -> bool:
        try:
            myCursor = self.dbConnection.cursor() # creates cursor object
            myCursor.execute(f"INSERT INTO users(username, password) VALUES({username}, {password})") # inserts username, password and totp secret into database
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

    def refreshAuthToken(self, username, type="access"):
        """
        Generate a new auth token (access or refresh) for a given username.
        - access: expires in 5 minutes
        - refresh: expires in 7 days
        Checks for an existing valid token and reuses it if valid.
        """
        try:
            with self.conn.cursor() as cur:
                # Check for existing token
                cur.execute(
                    "SELECT token, expires_at FROM auth_tokens WHERE username = %s AND token_type = %s",
                    (username, type)
                )
                row = cur.fetchone()

            if row:
                token, expires_at = row
                # Verify token validity
                is_valid, _ = self.verifyAuthToken(token, type=type)
                if is_valid:
                    return token  # Return existing valid token

            # Generate a new token
            token = secrets.token_urlsafe(32)
            if type == "access":
                expiresAt = int(time.time()) + 300  # 5 minutes
            elif type == "refresh":
                expiresAt = int(time.time()) + 7 * 24 * 3600  # 7 days
            else:
                raise ValueError("Invalid token type. Must be 'access' or 'refresh'.")

            with self.conn.cursor() as cur:
                # Use UPSERT with composite primary key
                cur.execute(
                    """
                    INSERT INTO auth_tokens (username, token, token_type, expires_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE token = VALUES(token), expires_at = VALUES(expires_at)
                    """,
                    (username, token, type, expiresAt)
                )
                self.conn.commit()

            return token  # Return the new token

        except Exception as e:
            return None

    def verifyAuthToken(self, token, type="access"):
        """
        Verify a token (access or refresh).
        Returns (True, username) if valid, else (False, None).

        - Access tokens: validity check + sliding expiration (extend 5 minutes).
        - Refresh tokens: validity check only (fixed lifetime).
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT expires_at, username FROM auth_tokens WHERE token = %s AND token_type = %s",
                    (token, type)
                )
                row = cur.fetchone()

            if row is None:
                return False, None

            expires_at, username = int(row[0]), row[1]
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

'''
def log(conn, username, verify, logReason) -> None:
    myCursor = conn.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.now(), verify,)) # inserts log of the users action into the database
    dbConnection.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    return
