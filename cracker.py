import secrets
from argon2 import PasswordHasher
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
ph = PasswordHasher()
x = ph.hash('a11c0d0f88415d0e3efc23c44e4d11f6581b89ef1be0db9979ae202bea75d9b0')
print(x)