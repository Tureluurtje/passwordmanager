import string
import random
import mysql.connector
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
import base64

class PasswordManager:
    def __init__(self, dbConnection):
        if dbConnection is None:
            return "Database connection is not valid", 500
        self.dbConnection = dbConnection
        
    def add_password(self, token, account_name, account_username, account_password):
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
            db = self.connectToDatabase()
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
            return "Password added successfully", 200
        except mysql.connector.Error as err:
            return "Databse connection error", 500
        
    def get_password(self, username):
        try:
            db = self.connectToDatabase()
            mycursor = db.cursor()
            query = "SELECT * FROM passwords WHERE username = %s"
            values = (username,)
            mycursor.execute(query, values)
            results = mycursor.fetchall()
            return results, 200
        except mysql.connector.Error as err:
            return "Database connection error", 500

    #TODO add function
    def delete_password(self, user, master_password, account_name):
        # Implement the logic to delete the password
        pass
    
    #TODO add function
    def update_password(self, user, master_password, account_name, account_password):
        # Implement the logic to update the password
        pass