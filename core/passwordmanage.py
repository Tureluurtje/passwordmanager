import mysql.connector
from mysql.connector import CMySQLConnection
import json
import base64
import datetime

class PasswordManager:
    def __init__(self, conn):
        if isinstance(conn, CMySQLConnection):
            self.conn = conn
        else:
            return "Database connection error", 500 
        
    def add_password(self, username, payload):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT vault FROM passwords WHERE username=%s", (username, ))
                row = cur.fetchone()
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
                    cur.execute("UPDATE passwords SET vault=%s WHERE username=%s", (updated_blob, username))
                else:
                    cur.execute("INSERT INTO passwords (username, vault) VALUES (%s, %s)", (username, updated_blob))
                self.conn.commit()
                return "Password added successfully", 200
        except Exception as err:
            return f"Database connection error: {err}", 500
        
    def get_password(self, username):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT vault FROM passwords WHERE username = %s LIMIT 1", (username,))
                (vault_blob, ) = cur.fetchone()
            vault_decoded = bytes(vault_blob).decode("utf-8")
            return vault_decoded, 200
        except mysql.connector.Error as err:
            return "Database connection error", 500

    def update_password(self, username, passwordId, replacements: dict):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT vault FROM passwords WHERE username=%s", (username,))
                row = cur.fetchone()

                if row:
                    existing_blob = row[0]
                    try:
                        passwords = json.loads(existing_blob)
                    except json.JSONDecodeError:
                        passwords = []
                else:
                    passwords = []

                updated = False
                for entry in passwords:
                    if entry.get("id") == passwordId:
                        # Update metadata fields
                        for key, value in replacements.items():
                            if "metadata" in entry and key in entry["metadata"]:
                                entry["metadata"][key] = value
                            else:
                                # Optionally allow adding new keys
                                entry["metadata"][key] = value  
                        # Also bump modified timestamp automatically
                        entry["metadata"]["modified"] = datetime.utcnow().isoformat() + "Z"
                        updated = True
                        break

                if not updated:
                    return f"No password entry found with id {passwordId}", 404

                # Save updated vault back to the database
                updated_blob = json.dumps(passwords)
                cur.execute("UPDATE passwords SET vault=%s WHERE username=%s", (updated_blob, username))
                self.conn.commit()
                return "Password updated successfully", 200
        except Exception as e:
            return f"There was an error updating your password: {str(e)}", 500

    def delete_password(self, username, passwordId):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT vault FROM passwords WHERE username=%s", (username,))
                row = cur.fetchone()
                
                if row:
                    existing_blob = row[0]
                    try:
                        passwords = json.loads(existing_blob)
                    except json.JSONDecodeError:
                        passwords = []
                else:
                    passwords = []

                # Update the isBreached field for the matching password entry
                updated = False
                for entry in passwords:
                    if entry.get("id") == passwordId:
                        passwords.remove(entry)
                        updated = True
                        break
                
                if not updated:
                    return f"No password entry found with id {passwordId}", 404

                # Save updated vault back to the database
                updated_blob = json.dumps(passwords)
                cur.execute("UPDATE passwords SET vault=%s WHERE username=%s", (updated_blob, username))
                self.conn.commit()
                return "Password removed successfully", 200
        except Exception as e:
            return f"There was an error deleting your password: {str(e)}", 500