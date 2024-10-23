import configparser
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

def connectToDatabase():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(root_dir, '..', 'config/config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    mydb = mysql.connector.connect(
    host=config['database']['host'],
    user=config['database']['user'],
    password=config['database']['password'],
    database=config['database']['db']
    ) # creates connection to database using a config file
    return mydb 
    


def addpass(user, masterpass, namepass, password):
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
    def encrypt_password(password, master_password):
            key = generate_key(master_password)
            fernet = Fernet(key)
            encrypted_password = fernet.encrypt(password.encode())
            return encrypted_password
    try:
        db = connectToDatabase()
        mycursor = db.cursor()
        if password:
            pass
        else:
            password = generatepassword()
        encrypted_password = encrypt_password(password, masterpass)
        query = "INSERT INTO passwords(user, namepass, encrypted_password) VALUES(%s, %s, %s)"
        values = (user, namepass, encrypted_password,)
        mycursor.execute(query, values)
        db.commit()
        log = True
        return True, log
    except mysql.connector.Error as err:
        log = False
        return False, log
