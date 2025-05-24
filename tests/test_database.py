from mysql.connector.connection_cext import CMySQLConnection
from core.passwordmanage import connect_to_database

def test_connection():
    assert isinstance(connect_to_database(), CMySQLConnection), "Expected a CMySQLConnection object"