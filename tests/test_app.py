import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Hello from the DSI ERD Flask app' in rv.data


def test_health(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200
    assert rv.get_json() == {'status': 'ok'}
