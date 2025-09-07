import hashlib
import json

def fetchSalt(username, conn):
    cur = conn.cursor()
    cur.execute("SELECT salt FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    
    if result:
        return result[0]
    else:
        return hashlib.sha256(username.encode()).hexdigest()[:32]

import json

def setBreached(username, passwordId, value, conn):
    cur = conn.cursor()
    
    # Fetch the existing vault for the user
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
            entry["metadata"]["isBreached"] = value
            updated = True
            break
    
    if not updated:
        return f"No password entry found with id {passwordId}", 404

    # Save updated vault back to the database
    updated_blob = json.dumps(passwords)
    cur.execute("UPDATE passwords SET vault=%s WHERE username=%s", (updated_blob, username))
    conn.commit()

    return "Password breach status updated successfully", 200
