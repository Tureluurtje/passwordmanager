import os
import configparser
import mysql.connector

def connectToDatabase():
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(root_dir, '..', 'config/config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        mydb = mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['db']
        ) # creates connection to database using a config file
        return mydb 
    except mysql.connector.Error as e:
        return e