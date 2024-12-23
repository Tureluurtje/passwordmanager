import configparser
import hashlib
import datetime
import os
import string
import random
import mysql.connector
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
import base64

def connect_to_database():
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(root_dir, '..', 'config/config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        mydb = mysql.connector.connect(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            database=config['database']['db']
        )
        return mydb 
    except mysql.connector.Error as e:
        return None

def login(username, password):
    conn = connect_to_database()
    if not conn:
        return False, None, "Database connection failed"
    
    mycursor = conn.cursor()
    query_failed_attempts = """
        SELECT COUNT(*) 
        FROM log 
        WHERE user = %s
        AND action = 'login'
        AND verify = 0
        AND date >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
    """
    mycursor.execute(query_failed_attempts, (username,))
    failed_login_attempts = mycursor.fetchone()[0]
    if failed_login_attempts >= 5:
        mycursor.execute(f"SELECT TIME_FORMAT(TIMEDIFF((DATE_SUB(NOW(6), INTERVAL 10 MINUTE)), (SELECT date from log WHERE user='{username}' AND verify='0' ORDER BY date DESC LIMIT 1)), '%i:%s') AS TIME_DIFFERENCE;")
        time_difference = mycursor.fetchone()[0]
        return False, None, f"Too many failed login attempts. Please try again in {time_difference[1:]} "
    
    master_password = hashlib.sha256(username.encode() + password.encode()).hexdigest()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    query_login = """
        SELECT COUNT(*)
        FROM users
        WHERE username = %s
        AND password = %s
    """
    mycursor.execute(query_login, (username.lower(), hashed_password))
    result = mycursor.fetchone()
    is_logged_in = result[0] > 0 if result is not None else False
    conn.close()
    return is_logged_in, master_password, True

def register(username, password):
    try:
        conn = connect_to_database()
        if not conn:
            return False
        
        mycursor = conn.cursor()
        mycursor.execute(f"INSERT INTO users(username, password) VALUES('{username}', '{hashlib.sha256(password.encode()).hexdigest()}')")
        conn.commit()
        mycursor.close()
        conn.close()
        return True
    except:
        return False

def log(username, verify, log_reason):
    conn = connect_to_database()
    if not conn:
        return
    
    mycursor = conn.cursor()
    mycursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, log_reason, datetime.datetime.now(), verify,))
    conn.commit()
    mycursor.close()
    conn.close()

def add_password(username, master_password, account_name, account_username, account_password):
    def generatepassword():
        lowercase_chars = string.ascii_lowercase
        uppercase_chars = string.ascii_uppercase
        digits = string.digits
        special_chars = string.punctuation
        all_chars = lowercase_chars + uppercase_chars + digits + special_chars
        password_parts = []
        for _ in range(4):
            part = ''.join(random.choices(all_chars, k=4))
            password_parts.append(part)
        password = '-'.join(password_parts)
        return password
    def generate_key(master_password):
        salt = b'salt_'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1000000,
            backend=default_backend()
        )
        key = kdf.derive(master_password.encode())
        key_base64 = base64.urlsafe_b64encode(key)
        return key_base64
    def encrypt_password(account_password, master_password):
            key = generate_key(master_password)
            fernet = Fernet(key)
            encrypted_password = fernet.encrypt(account_password.encode())
            return encrypted_password
    try:
        db = connect_to_database()
        mycursor = db.cursor()
        if account_password != '':
            pass
        else:
            account_password = generatepassword()
        encrypted_password = encrypt_password(account_password, master_password)
        query = "INSERT INTO passwords(username, account_name, account_username, account_password) VALUES(%s, %s, %s, %s)"
        values = (username, account_name, account_username, account_password,)
        mycursor.execute(query, values)
        db.commit()
        log = True
        return True, log
    except mysql.connector.Error as err:
        error = err
        log = False
        return False, log

def get_password(user, master_password, account_name):
    # Implement the logic to get the password
    pass

def delete_password(user, master_password, account_name):
    # Implement the logic to delete the password
    pass

def update_password(user, master_password, account_name, account_password):
    # Implement the logic to update the password
    pass