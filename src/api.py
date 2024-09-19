from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc, exc
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)
swagger = Swagger(app, template={
    "info": {
        "title": "Message Service REST API",
        "description": "A simple API for sending and fetching messages.",
        "version": "1.0.0"
    },
})

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    # For debugging purposes
    def __repr__(self):
        return f'<Message(id={self.id}, sender={self.sender}, recipient={self.recipient}, content={self.content}, timestamp={self.timestamp}, is_read={self.is_read})>'

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'content': self.content,
            'timestamp': self.timestamp,
            'is_read': self.is_read
        }

@app.route('/messages', methods=['POST'])
def send_message():
    """
    Send a message to a user.
    ---
    tags:
        - messages
    parameters:
    - in: body
      name: body
      required: true
      description: JSON payload containing the message details.
      schema:
        type: object
        properties:
          sender:
            type: string
            description: The identifier of the sender user (username).
          recipient:
            type: string
            description: The identifier of the recipient user (username).
          content:
            type: string
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

    try:
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'message': 'Message sent successfully'}), 201
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error. Please try again.'}), 500
    

@app.route('/messages/new', methods=['GET'])
def fetch_new_messages():
    """
    Fetch new messages for a user.
    Only fetches messages that have not been read yet.
    ---
    tags:
        - messages
    parameters:
        - name: recipient
          in: query
          type: string
          required: true
          description: The identifier of the recipient user (username).
    responses:
        200:
            description: A list of new unfetched messages for the recipient user (if existent).
        400:
            description: Missing required fields.
    """
    data = request.args

    if 'recipient' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    try: 
        messages = Message.query.filter_by(recipient=data['recipient'], is_read=False).all()

        # Seralize messages
        messages_list = [message.to_dict() for message in messages] 
        for message in messages_list:
            message.pop('is_read') # Not really relevant for this response. 

        if not messages_list:
            return jsonify({'messages': [], "info":f'No new messages found for {data["recipient"]}'}), 200
        
        # Mark messages as read
        for message in messages:
            message.is_read = True
            db.session.commit()
        
        return jsonify({'messages': messages_list}), 200
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error. Please try again.'}), 500

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    """
    Delete a single message by its ID.
    ---
    tags:
        - messages
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
    try: 
        message = db.session.get(Message, id)

        if message is None:
            return jsonify({'error': 'Message not found'}), 404
        
        message_details = message.to_dict()
        
        db.session.delete(message)
        db.session.commit()

        return jsonify({'message': 'Message deleted successfully', "deleted_message": message_details}), 200
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error. Please try again.'}), 500

 
# NOTE: Design choice: All messages must exist, or none will be deleted.
@app.route('/messages', methods=['DELETE'])
def delete_multiple_messages():
    """
    Delete multiple messages by their IDs.
    Only deletes messages if all given IDs exist.
    ---
    tags:
        - messages
    parameters:
    - in: body
      name: body
      required: true
      description: JSON payload containing the IDs.
      schema:
        type: object
        properties:
          ids:
            type: array
            items:
                type: integer
            description: A string representation of a list of IDs (e.g., "[1,2]").
    responses:
        200:
            description: Messages deleted successfully.
        400:
            description: Missing required fields.
        404:
            description: One or more messages were not found.
    """
    data = request.get_json()

    if 'ids' not in data or not data['ids']:
        return jsonify({'error': 'Missing required fields'}), 400

    ids = data['ids']
    try: 
        messages_to_delete = Message.query.filter(Message.id.in_(ids)).all()
        found_ids = [message.id for message in messages_to_delete]
        not_found_ids = list(set(ids) - set(found_ids))

        if not_found_ids:
            return jsonify({'error': f'Messages not found', 'not_found_ids':f'{not_found_ids}'}), 404
        
        Message.query.filter(Message.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()

        return jsonify({'message': f'Successfully deleted all messages'}), 200
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error. Please try again.'}), 500


@app.route('/messages', methods=['GET'])
def fetch_messages():
    """
    Fetch multiple messages for a user.
    Fetches messages based on the recipient user and the start and stop indexes in descending order, regardless of whether the messages has been read or not.
    If stop_index is greater than the total number of messages, the response will contain all messages from start_index to the last message.
    ---
    tags:
        - messages
    parameters:
      - name: recipient
        in: query
        type: string
        required: true
        description: The identifier of the recipient user (username).
      - name: start_index
        in: query
        type: integer
        required: false
        default: 0
        description: The start index of the messages to fetch (inclusive).
      - name: stop_index
        in: query
        type: integer
        required: false
        default: 50
        description: The stop index of the messages to fetch (exclusive).
    responses:
        200:
            description: A list of messages for the recipient user (if existent).
        400:
            description: Missing required fields.
    """
    recipient = request.args.get('recipient')
    start_index = request.args.get('start_index', default=0, type=int)
    stop_index = request.args.get('stop_index', default=50, type=int)

    # Validate input
    if recipient is None:
        return jsonify({'error': 'Missing recipient parameter'}), 400
    if start_index < 0 or stop_index < 0:
        return jsonify({'error': 'Indexes must be positive integers'}), 400
    if start_index > stop_index:
        return jsonify({'error': 'Start index must be less than stop index'}), 400
    
    try:
        query = Message.query.filter_by(recipient=recipient).order_by(desc(Message.timestamp))
        messages = query.slice(start_index, stop_index).all()

        messages_list = [message.to_dict() for message in messages]

        return jsonify({'messages': messages_list,
                        'total_messages': len(messages),
                        'start_index': start_index,
                        'stop_index': stop_index
                    }), 200
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error. Please try again.'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)