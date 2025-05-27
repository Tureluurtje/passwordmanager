import string
import random
import mysql.connector
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
import base64

from core.connection import connectToDatabase
from core.logup import AuthenticationManager

class PasswordManager:
    def __init__(self, username=None, master_password=None):
        if username is None or master_password is None:
            return ["Username and master password must be provided.", 400]
        userAuthenticated = AuthenticationManager.login(username, master_password)
        if userAuthenticated == False:
            return ["Authentication failed. Please check your credentials.", 401]
        return
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
            db = connectToDatabase()
            mycursor = db.cursor()
            if account_password != '':
                pass
            else:
                account_password = generatepassword()
            encrypted_password = encrypt_password(account_password, master_password)
            query = "INSERT INTO passwords(username, account_name, account_username, account_password) VALUES(%s, %s, %s, %s)"
            values = (username, account_name, account_username, encrypted_password,)
            mycursor.execute(query, values)
            db.commit()
            log = True
            return True, log
        except mysql.connector.Error as err:
            error = err
            log = False
            return False, log

    def get_password(user, master_password, account_name):
        try:
            db = connectToDatabase()
            mycursor = db.cursor()
            query = "SELECT account_password FROM passwords WHERE username = %s AND account_name = %s"
        except:
            pass
        pass

    def delete_password(user, master_password, account_name):
        # Implement the logic to delete the password
        pass

    def update_password(user, master_password, account_name, account_password):
        # Implement the logic to update the password
        pass