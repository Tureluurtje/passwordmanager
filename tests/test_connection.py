import requests

from mysql.connector.connection_cext import CMySQLConnection

from core.passwordmanage import connect_to_database

def test_database_connection():
    assert isinstance(connect_to_database(), CMySQLConnection), "Expected a CMySQLConnection object"

def test_server_connection():
    response = requests.get("http://127.0.0.1:5000/ping")
    assert (response.json() == "pong" and response.status_code == 200), "Could not establish server connection"
