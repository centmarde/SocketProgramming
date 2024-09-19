from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import sqlite3
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

socketio = SocketIO(app, cors_allowed_origins="*")  # Allow CORS for socket connections

# Array of random responses
random_responses = [
    "Got it!",
    "Interesting!",
    "Tell me more!",
    "I agree!",
    "Let's discuss!",
    "Sounds good!"
]

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    response TEXT
                 )''')
    conn.commit()
    conn.close()

# Route to fetch all messages (user and bot responses)
@app.route('/messages', methods=['GET'])
def get_messages():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT content, response FROM messages')
    messages = [{'message': row[0], 'response': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(messages)

# Handle incoming socket messages and store them along with random responses
@socketio.on('send_message')
def handle_message(data):
    user_message = data['message']
    bot_response = random.choice(random_responses)

    # Save user message and bot response in database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (content, response) VALUES (?, ?)', (user_message, bot_response))
    conn.commit()
    conn.close()

    # Emit the new message and bot response to all connected clients
    socketio.emit('new_message', {'message': user_message, 'response': bot_response})

# Main entry point for the Flask app
if __name__ == '__main__':
    init_db()  # Initialize the database
    socketio.run(app, host='localhost', port=5000, debug=True)
