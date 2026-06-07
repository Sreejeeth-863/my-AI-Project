from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

@app.route('/')
def serve_index():
    """Serve the React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and call Anthropic API"""
    try:
        data = request.json
        character_personality = data.get('personality')
        user_message = data.get('message')
        character_name = data.get('character_name')
        
        if not character_personality or not user_message or not character_name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Call Anthropic API
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=300,
            messages=[
                {
                    'role': 'user',
                    'content': f"{character_personality}\n\nChild says: \"{user_message}\"\n\nRespond as {character_name} in a way that's helpful, warm, and age-appropriate."
                }
            ]
        )
        
        ai_response = message.content[0].text
        return jsonify({'response': ai_response}), 200
        
    except Exception as error:
        print(f'Error: {error}')
        return jsonify({'error': 'Failed to process message'}), 500

@app.errorhandler(404)
def not_found(e):
    """Serve React app for all unmatched routes (for client-side routing)"""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
