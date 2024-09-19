from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import sqlite3
from groq import Groq

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

socketio = SocketIO(app, cors_allowed_origins="*")  # Allow CORS for socket connections

# Initialize the Groq client
client = Groq(api_key='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')

# Initialize an empty list to keep conversation history
conversation_history = []

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

# Handle incoming socket messages and generate responses from AI
@socketio.on('send_message')
def handle_message(data):
    global conversation_history
    MAX_HISTORY_LENGTH = 10

    user_message = data['message']
    
    # Add the new user message to the conversation history
    conversation_history.append({"role": "user", "content": user_message})

    # Limit the size of the conversation history
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        conversation_history.pop(0)

    # Generate a response from the AI using the Groq API
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=conversation_history + [{"role": "system", "content": "You must reply to any question that I ask."}],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    # Extract the AI response
    bot_response = completion.choices[0].message.content

    # Add the bot response to the conversation history
    conversation_history.append({"role": "assistant", "content": bot_response})

    # Save user message and AI response in database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (content, response) VALUES (?, ?)', (user_message, bot_response))
    conn.commit()
    conn.close()

    # Emit the new message and bot response to all connected clients
    socketio.emit('new_message', {'message': user_message, 'response': bot_response})

@socketio.on('clear_chat')
def clear_chat():
    # Clear the messages from the SQLite database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages')
    conn.commit()
    conn.close()

    # Clear the conversation history
    global conversation_history
    conversation_history = []

    # Emit an event to notify all clients to clear their chat history
    socketio.emit('chat_cleared')

# Main entry point for the Flask app
if __name__ == '__main__':
    init_db()  # Initialize the database
    socketio.run(app, host='localhost', port=5000, debug=True)
