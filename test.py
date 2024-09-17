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

# NOTE: Relies on send_message and fetch_new_messages
def test_delete_message(client):
    response = client.post('/messages', json={'sender': 'leifgw', 'recipient': 'kungen', 'content': 'Tjenare kungen!'})
    assert response.status_code == 201

    response = client.delete('/messages/1')
    assert response.status_code == 200

    response = client.get('/messages/new?recipient=kungen')
    assert response.status_code == 200
    assert response.json['messages'] == []

def test_delete_message_not_found(client):
    response = client.delete('/messages/1')
    assert response.status_code == 404

def test_delete_multiple(client):
    response = client.post('/messages', json={'sender': 'leifgw', 'recipient': 'kungen', 'content': 'Tjenare kungen!'})
    response = client.post('/messages', json={'sender': 'leifgw', 'recipient': 'kungen', 'content': 'Svara mig!'})

    response = client.delete('/messages', json={'ids': [1, 2]})
    assert response.status_code == 200

def test_delete_multiple_empty_ids(client):
    response = client.delete('/messages', json={'ids': None})
    assert response.status_code == 400

def test_delete_multiple_missing_ids(client):
    response = client.delete('/messages', json={'ids': [1, 2]})
    assert response.status_code == 404

def test_delete_multiple_partly_missing_ids(client):
    response = client.post('/messages', json={'sender': 'leifgw', 'recipient': 'kungen', 'content': 'Tjenare kungen!'})
    response = client.post('/messages', json={'sender': 'leifgw', 'recipient': 'kungen', 'content': 'Svara mig!'})

    response = client.delete('/messages', json={'ids': [1, 2, 3]})
    assert response.status_code == 404
    assert response.json['error'] == 'Messages not found'
    assert response.json['not_found_ids'] == '[3]'