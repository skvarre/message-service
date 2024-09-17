import pytest 
from api import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        db.drop_all()

def test_fetch_new_messages(client):
    response = client.get('/messages/new?recipient=leifgw')
    assert response.status_code == 200
    assert response.json['messages'] == []

def test_fetch_new_messages_missing_recipient(client):
    response = client.get('/messages/new')
    assert response.status_code == 400
    assert response.json['error'] == 'Missing required fields'

