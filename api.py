from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

# Send a message to a user.
@app.route('/messages', methods=['POST'])
def send_message():
    pass

# Get NEW messages.
@app.route('/messages/new', methods=['GET'])
def fetch_new_messages():
    pass

# Delete message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    pass

# Delete multiple messages
@app.route('/messages', methods=['DELETE'])
def delete_multiple_messages():
    pass

# Get ALL messages.
@app.route('/messages', methods=['GET'])
def fetch_messages():
    pass


if __name__ == '__main__':
    app.run(debug=True)