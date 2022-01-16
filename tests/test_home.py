import pytest
from app_info_about_movies import app, routes

@pytest.fixture
def client():
    return app.test_client()

def test_home(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/html'

def test_home_bad_http_method(client):
    resp = client.post('/')
    assert resp.status_code == 405  # 405 = Method Not Allowed 

    
