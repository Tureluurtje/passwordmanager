import mysql.connector
from mysql.connector import CMySQLConnection, MySQLConnection
import json
import base64
import datetime

class PasswordManager:
    def __init__(self, dbConnection):
        if isinstance(dbConnection, (CMySQLConnection, MySQLConnection)):
            self.dbConnection = dbConnection
        else:
            return "Database connection error", 500 
        
    def add_password(self, username, payload):
        try:
            db = self.dbConnection
            mycursor = db.cursor()
            mycursor.execute("SELECT vault FROM passwords WHERE username=%s", (username, ))
            row = mycursor.fetchone()
            if row:
                existing_blob = row[0]
                try:
                    passwords = json.loads(existing_blob)
                except json.JSONDecodeError:
                    passwords = []

            else:
                passwords = []
            
            passwords.append(payload)
            
            # use helper to ensure any bytes or datetimes in the payload are encoded
            updated_blob = json.dumps(passwords)
            if row:
                mycursor.execute("UPDATE passwords SET vault=%s WHERE username=%s", (updated_blob, username))
            else:
                mycursor.execute("INSERT INTO passwords (username, vault) VALUES (%s, %s)", (username, updated_blob))
            db.commit()
            return "Password added successfully", 200
        except Exception as err:
            return f"Database connection error: {err}", 500
        
    def get_password(self, username):
        try:
            db = self.dbConnection
            mycursor = db.cursor()
            query = "SELECT vault FROM passwords WHERE username = %s LIMIT 1"
            values = (username,)
            mycursor.execute(query, values)
            (vault_blob, ) = mycursor.fetchone()
            vault_decoded = bytes(vault_blob).decode('utf-8')
            return vault_decoded, 200
        except mysql.connector.Error as err:
            return "Database connection error", 500

    def delete_password(self, user, master_password, account_name):
        # Implement the logic to delete the password
        pass
    
    #TODO add function
    def update_password(self, user, master_password, account_name, account_password):
        # Implement the logic to update the password
        pass