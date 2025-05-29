import hashlib
import datetime

class AuthenticationManager:
    def __init__(self, connectToDatabase=None):
        if connectToDatabase :
            self.connectToDatabase = connectToDatabase
        else:
            raise ValueError("connectToDatabase function is required")
        
    def login(self, username, password):
        logAttempt = True
        login_succes = False
        conn = self.connectToDatabase()
        myCursor = conn.cursor()  # creates cursor object
        query_failed_attempts = """
            SELECT COUNT(*) 
            FROM log 
            WHERE user = %s
            AND action = 'login'
            AND verify = 0
            AND date >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
        """
        myCursor.execute(query_failed_attempts, (username,)) # Check for failed login attempts of username in the last 10 minutes
        failedLoginAttempts = myCursor.fetchone()[0]  # fetch failed login attempts
        if failedLoginAttempts >= 5: # If more than 5 failed login attempts, exit
            myCursor.execute(f"SELECT TIME_FORMAT(TIMEDIFF((DATE_SUB(NOW(6), INTERVAL 10 MINUTE)), (SELECT date from log WHERE user='{username}' AND verify='0' ORDER BY date DESC LIMIT 1)), '%i:%s') AS TIME_DIFFERENCE;")
            logAttempt = False
            time_difference = myCursor.fetchone()[0]
            logAttempt = (f"Too many failed login attempts. Please try again in {time_difference[1:]} ")
        else:
            masterPassword = hashlib.sha256(username.encode() + password.encode()).hexdigest()  # hashed username + password
            hashedPassword = hashlib.sha256(password.encode()).hexdigest() # hashed password only
            query_login = """
                SELECT COUNT(*)
                FROM users
                WHERE username = %s
                AND password = %s
            """
            myCursor.execute(query_login, (username.lower(), hashedPassword)) # Check if the username and hashed password exist in the database
            result = myCursor.fetchone()
            login_succes = result[0] > 0 if result is not None else False  # Check if match found
        conn.close() # Close the connection
        return (True, masterPassword) if login_succes else (False, None) # Return the result: True if successful login, False otherwise

    def register(self, username, password) -> None:
        try:
            conn = self.connectToDatabase()
            myCursor = conn.cursor() # creates cursor object
            myCursor.execute(f"INSERT INTO users(username, password) VALUES('{username}', '{hashlib.sha256(password.encode()).hexdigest()}')") # inserts username, password and totp secret into database
            conn.commit()  # Commit on the same connection
            myCursor.close()  # Close cursor
            conn.close()  # Close connection
            return True
        except:
            return False
    
def log(conn, username, verify, logReason) -> None:
    myCursor = conn.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.datetime.now(), verify,)) # inserts log of the users action into the database
    conn.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    conn.close()  # Close connection
    return
