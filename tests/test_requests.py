import requests
import pytest

@pytest.fixture(scope='module')
def test_connection():
    response = requests.get('http://127.0.0.1:5000/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello, World!'}
    return response
    
def test_connection_json(test_connection):
    assert test_connection.headers['Content-Type'] == 'application/json'

def test_connection_2():
    response = requests.get('http://127.0.1:5000/ping')
    assert response.status_code == 200
    assert response.json() == {'message': 'pong'}