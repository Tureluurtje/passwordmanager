import requests
import pytest

def test_connection():
    response = requests.get('http://127.0.0.1:5000/')
    assert response.status_code == 200, "Expected status code 200"
    assert response.headers['Content-Type'] == 'application/json', "Expected Content-Type to be application/json"
    assert response.json() == {'message': 'Hello, World!'}, "Expected response to be {'message': 'Hello, World!'}"

def test_connection_2():
    response = requests.get('http://127.0.1:5000/ping')
    assert response.status_code == 200
    assert response.json() == {'message': 'pong'}
    
@pytest.mark.xfail()
def test_api():
    response = requests.get('http://127.0.1:5000/api/')
    assert response.status_code == 200, "Expected status code 200"
    
def test_authentication():
    response = requests.get(
        'http://127.0.1:5000/api/',
        json={
            "username": "testuser", 
            "password": "testpassword"
              }
    )
    assert response.status_code == 200, "Expected status code 200"