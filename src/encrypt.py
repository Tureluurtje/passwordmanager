import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

def verify_password(hashed_password, password):
    return bcrypt.checkpw(password.encode(), hashed_password)

# Example usage
password = "mysecretpassword"
hashed_password = hash_password(password)
print("Hashed Password:", hashed_password)

# Verifying password
print("Password Verified:", verify_password(hashed_password, password))
