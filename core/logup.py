import configparser
import mysql.connector
import hashlib
import datetime
import os
import pyotp
import qrcode
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Label

def connectToDatabase():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(root_dir, '..', 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    mydb = mysql.connector.connect(
    host=config['database']['host'],
    user=config['database']['user'],
    password=config['database']['password'],
    database=config['database']['db']
    ) # creates connection to database using a config file
    return mydb 
def login(username, password, code):
    logAttempt = True
    login_succes = False
    code_verify = False
    conn = connectToDatabase()
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
        logAttempt = (f"Too many failed login attempts. Please try again in {time_difference[1:]}.")
    else:
        verify_totp = verifyTotp(username, code)
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
        code_verify = True if verify_totp else False
        login_succes = result[0] > 0 if result is not None else False  # Check if match found
    conn.close() # Close the connection
    return (True, masterPassword, logAttempt) if login_succes and code_verify else (False, None, logAttempt) # Return the result: True if successful login, False otherwise
def register(username, password) -> None:
    try:
        secret = generateTotp(username)
        conn = connectToDatabase()
        myCursor = conn.cursor() # creates cursor object
        myCursor.execute(f"INSERT INTO users(username, password, totpSecret) VALUES('{username}', '{hashlib.sha256(password.encode()).hexdigest()}', '{secret}')") # inserts username, password and totp secret into database
        conn.commit()  # Commit on the same connection
        myCursor.close()  # Close cursor
        conn.close()  # Close connection
        return True
    except:
        return False
def log(username, verify, logReason) -> None:
    conn = connectToDatabase()
    myCursor = conn.cursor() #creates cursor object
    myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.datetime.now(), verify,)) # inserts log of the users action into the database
    conn.commit()  # Commit on the same connection
    myCursor.close()  # Close cursor
    conn.close()  # Close connection
    return
def generateTotp(username):
    secret = pyotp.random_base32() # generates a secret key
    totp = pyotp.TOTP(secret) # create TOTP
    provisioningUrl = totp.provisioning_uri(username, issuer_name="Password Manager") # generate provisioning URL
    qr = qrcode.make(provisioningUrl) # Generates QR code and keeps in memory
    imgBytes = BytesIO()
    qr.save(imgBytes, format="PNG") # save QR code to memory
    imgBytes.seek(0)
    root = Tk() # create Tkinter object
    root.title("Please scan this code with your authenticator app") # sets title for window
    image = Image.open(imgBytes) # opens image from memory
    tkImage = ImageTk.PhotoImage(image) # covert QR code to image Tkinter can display
    label = Label(root, image=tkImage) # craetes Label widget in Tkinter to hold the QR code
    label.pack()
    root.mainloop() # runs tkinter event loop
    return secret # returns secret key
def verifyTotp(username, code):
    conn = connectToDatabase()
    myCursor = conn.cursor()  # Create cursor object
    query = "SELECT totpSecret FROM users WHERE username = %s"
    myCursor.execute(query, (username,))  # Execute the query with parameterized input
    result = myCursor.fetchone() # Fetch the result and handle if no secret is found
    is_verified = False
    secret = result[0]  # Get the TOTP secret from the result
    totp = pyotp.TOTP(secret) # Generate the TOTP object using the secret
    is_verified = totp.verify(code) # Verify the code and return the result
    conn.close() # Close the connection and return the result
    return is_verified