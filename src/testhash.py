import hashlib
x = hashlib.sha256('testpassword'.encode()).hexdigest()
print(x)