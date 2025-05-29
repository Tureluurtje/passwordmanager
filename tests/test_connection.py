import requests

from mysql.connector.connection_cext import CMySQLConnection

from core.server import connectToDatabase

def test_database_connection():
    conn = connectToDatabase()
    assert isinstance(conn, CMySQLConnection), "Expected a CMySQLConnection object"