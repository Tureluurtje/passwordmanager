import secrets

salt = secrets.token_hex(16)  # 16 bytes -> 32 hex characters
print(salt)

'''
import mysql.connector

with open("/Users/Tureluurtje/Downloads/rockyou.txt", "r", encoding="utf-8", errors="ignore") as f:
    data = f.readlines()


for line in data:
    try:
        mysql.connector.connect(
            host="localhost",
            user="develop",
            password=line.strip(),
            database="passafe"
        )
        print(line.strip())
        Break
    except:
        pass
'''