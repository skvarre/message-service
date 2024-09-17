from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    # For debugging purposes
    def __repr__(self):
        return f'<Message(id={self.id}, sender={self.sender}, recipient={self.recipient}, content={self.content}, timestamp={self.timestamp}, is_read={self.is_read})>'

# Send a message to a user
@app.route('/messages', methods=['POST'])
def send_message():
    """
    Send a message to a user.
    
    ---
    parameters:
        - name: sender
            in: body
            type: string
            required: true
            description: The identifier of the sender user (username).
        - name: recipient
            in: body
            type: string
            required: true
            description: The identifier of the recipient user (username).
        - name: content
            in: body
            type: string
            required: true
            description: The content of the message.
    responses:
        201:
            description: Message sent successfully.
        400:
            description: Missing required fields.
    """
    data = request.get_json() 

    # Check if the required fields are present
    if any(field not in data for field in ['sender', 'recipient', 'content']):
            return jsonify({'error': 'Missing required fields'}), 400
    
    new_message = Message(
        sender=data['sender'],
        recipient=data['recipient'],
        content=data['content']
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully'}), 201

# Get NEW messages
@app.route('/messages/new', methods=['GET'])
def fetch_new_messages():
    """
    Fetch new messages for a user.

    ---
    parameters:
        - name: recipient
            in: query
            type: string
            required: true
            description: The identifier of the recipient user (username).
    responses:
        200:
            description: A list of new unfetched messages for the recipient user if existent.
        400:
            description: Missing required fields.
    """
    data = request.args

    if 'recipient' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    messages = Message.query.filter_by(recipient=data['recipient'], is_read=False).all()

    # Seralize messages
    messages_list = []

    for message in messages:
        messages_list.append({
            'id': message.id,
            'sender': message.sender,
            'recipient': message.recipient,
            'content': message.content,
            'timestamp': message.timestamp,
            # 'is_read': message.is_read -- Not really relevant for this endpoint
        })

    if messages_list == []:
        return jsonify({'messages': [], "info":f'No new messages found for {data["recipient"]}'}), 200
    
    # Mark messages as read
    for message in messages:
        message.is_read = True
        db.session.commit()
    
    return jsonify({'messages': messages_list}), 200

# Delete message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    """
    Delete a message by its ID.
    
    ---
    parameters:
        - name: id
            in: path
            type: integer
            required: true
            description: The identifier of the message to be deleted.
    responses:
        200:
            description: Message deleted successfully.
        404:
            description: Message not found.
    """
    message = Message.query.get(id)

    if message is None:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()

    return jsonify({'message': 'Message deleted successfully'}), 200

# Delete multiple messages
@app.route('/messages', methods=['DELETE'])
def delete_multiple_messages():
    pass

# Get ALL messages.
@app.route('/messages', methods=['GET'])
def fetch_messages():
    pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)