import face_recognition
import cv2
import configparser
import io
import mysql.connector
import hashlib
import string
import base64
import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyboard
import time
import curses
import os
import random
import pyperclip
import pyotp

ConfigLocation = 'database~2024-05-18~arthu.ini'
config = configparser.ConfigParser()

def connectToDatabase():
    config.read(ConfigLocation)
    mydb = mysql.connector.connect(
    host=config.get('dblogin', 'host'),
    user=config.get('dblogin', 'user'),
    password=config.get('dblogin', 'password'),
    database=config.get('dblogin', 'db')
    ) # creates connection to database using a config file
    return mydb 
class logup:
    def login(username, password):
        myCursor = connectToDatabase().cursor() # creates cursor object
        myCursor.execute(f"""
            SELECT COUNT(*) 
            FROM log 
            WHERE user = '{username}' 
            AND action = 'attemptLogin'
            AND verify = 0
            AND date >= DATE_SUB(NOW(), INTERVAL 10 HOUR_MINUTE)
            """) # fetches for login history of username in database in past 10 minutes
        failedLoginAttempts = myCursor.fetchone()[0] # fetch failed login attempts
        if failedLoginAttempts > 5: # if failed login attempts exceed 5, print error message
            print("Too many failed login attempts. Please try again in 10 minutes from now.")
            exit()
        masterPassword = hashlib.sha256(username.encode()+password.encode()).hexdigest() # generates masterpassword of hashed username and password combined
        hashedPassword = hashlib.sha256(password.encode()).hexdigest() # generates hashed password of the given password
        myCursor.execute(f"""
            SELECT COUNT(*)
            FROM users
            WHERE username = '{username.lower()}'
            AND password = '{hashedPassword}""")
        return (True, masterPassword) if myCursor.fetchone()[0] > 0 else (False,) # if username and password match in database, verify and log the user in

    def log(username, verify, logReason):
        myCursor = connectToDatabase().cursor() #creates cursor object
        myCursor.execute(f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)", (username, logReason, datetime.datetime.now(), verify,)) # inserts log of the users action into the database
        connectToDatabase().commit() # commits the transaction

