import pytest
from app_info_about_movies import app, routes

@pytest.fixture
def client():
    return app.test_client()

def test_home(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/html'
