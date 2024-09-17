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

# NOTE: Relies on fetch_new_messages
def test_send_message(client):
    response = client.post('/messages', json={'sender': 'leifgw', 'recipient': 'kungen', 'content': 'Tjenare kungen!'})
    assert response.status_code == 201

    response = client.get('/messages/new?recipient=kungen')
    assert response.status_code == 200
    assert response.json['messages'][0]['sender'] == 'leifgw'
    assert response.json['messages'][0]['content'] == 'Tjenare kungen!'

def test_send_message_missing_fields(client):
    response = client.post('/messages', json={'sender': 'leifgw', 'content': 'Tjenare kungen!'})
    assert response.status_code == 400
    assert response.json['error'] == 'Missing required fields'

# NOTE: Relies on send_message and fetch_new_messages
def test_delete_message(client):
    response = client.post('/messages', json={'sender': 'leifgw', 'recipient': 'kungen', 'content': 'Tjenare kungen!'})
    assert response.status_code == 201

    response = client.delete('/messages/1')
    assert response.status_code == 200

    response = client.get('/messages/new?recipient=kungen')
    assert response.status_code == 200
    assert response.json['messages'] == []
