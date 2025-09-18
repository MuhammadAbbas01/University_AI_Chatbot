#!/usr/bin/env python3
"""
Flask Web Server for University of Malakand AI Chatbot
Provides REST API and web interface for the intelligent chatbot system
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
import logging
import os
from pathlib import Path
import threading
import time
from datetime import datetime

# Import your chatbot system
try:
    from data_scraper import UniversityDataScraper
    from uom_ai_chatbot import UniversityAIChatbot
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    print("⚠️ Chatbot modules not found. Running in demo mode.")

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global chatbot instance
chatbot_instance = None

# HTML template for the web interface
WEB_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>University of Malakand AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .chat-container {
            max-width: 900px;
            width: 100%;
            height: 600px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .chat-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }

        .user-message {
            align-self: flex-end;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .bot-message {
            align-self: flex-start;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            color: #333;
        }

        .bot-message strong {
            color: #1e3c72;
        }

        .typing-indicator {
            align-self: flex-start;
            padding: 12px 18px;
            background: #f8f9fa;
            border-radius: 18px;
            display: none;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: #999;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 10px;
        }

        .input-field {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            outline: none;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .input-field:focus {
            border-color: #667eea;
        }

        .send-button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .send-button:active {
            transform: translateY(0);
        }

        .quick-buttons {
            display: flex;
            gap: 10px;
            padding: 0 20px 20px;
            flex-wrap: wrap;
        }

        .quick-btn {
            padding: 8px 16px;
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            color: #667eea;
            transition: all 0.3s;
        }

        .quick-btn:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: translateY(-1px);
        }

        .status-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 10px;
            color: white;
            font-size: 14px;
            display: none;
        }

        .status-success {
            background: #28a745;
        }

        .status-error {
            background: #dc3545;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }

        @media (max-width: 768px) {
            .chat-container {
                height: 100vh;
                border-radius: 0;
                margin: 0;
            }
            
            .message {
                max-width: 90%;
            }
            
            .quick-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🎓 University of Malakand AI Assistant</h1>
            <p>Your intelligent guide to university information</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="bot-message">
                <strong>Welcome!</strong> I'm your University of Malakand AI Assistant. I can help you with information about faculty, departments, admissions, notifications, and more. How can I assist you today?
            </div>
        </div>

        <div class="quick-buttons">
            <div class="quick-btn" onclick="sendQuickMessage('Tell me about faculty')">Faculty Info</div>
            <div class="quick-btn" onclick="sendQuickMessage('Admission requirements')">Admissions</div>
            <div class="quick-btn" onclick="sendQuickMessage('Recent notifications')">Notifications</div>
            <div class="quick-btn" onclick="sendQuickMessage('Department information')">Departments</div>
            <div class="quick-btn" onclick="sendQuickMessage('Research information')">Research</div>
            <div class="quick-btn" onclick="sendQuickMessage('help')">Help</div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" class="input-field" id="messageInput" placeholder="Ask me anything about University of Malakand..." onkeypress="handleKeyPress(event)">
            <button class="send-button" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <div class="status-indicator" id="statusIndicator"></div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const typingIndicator = document.getElementById('typingIndicator');
        const statusIndicator = document.getElementById('statusIndicator');

        function addMessage(message, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
            
            // Format message with basic markdown-like formatting
            let formattedMessage = message
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
            
            messageDiv.innerHTML = formattedMessage;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTyping() {
            typingIndicator.style.display = 'block';
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTyping() {
            typingIndicator.style.display = 'none';
        }

        function showStatus(message, type) {
            statusIndicator.textContent = message;
            statusIndicator.className = `status-indicator status-${type}`;
            statusIndicator.style.display = 'block';
            setTimeout(() => {
                statusIndicator.style.display = 'none';
            }, 3000);
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, true);
            messageInput.value = '';

            // Show typing indicator
            showTyping();

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                hideTyping();
                addMessage(data.response);

            } catch (error) {
                hideTyping();
                addMessage('Sorry, I encountered an error. Please try again.', false);
                showStatus('Connection Error', 'error');
                console.error('Error:', error);
            }
        }

        function sendQuickMessage(message) {
            messageInput.value = message;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Auto-focus on input
        messageInput.focus();

        // Check server status on load
        window.addEventListener('load', async () => {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                showStatus(data.message, 'success');
            } catch (error) {
                showStatus('Server connection failed', 'error');
            }
        });
    </script>
</body>
</html>
"""

def initialize_chatbot():
    """Initialize the chatbot system"""
    global chatbot_instance
    
    if not CHATBOT_AVAILABLE:
        logger.warning("Chatbot modules not available. Running in demo mode.")
        return False
    
    try:
        # Check if knowledge base exists
        data_dir = Path("university_data")
        db_path = data_dir / "university_knowledge.db"
        
        if not db_path.exists():
            logger.info("Knowledge base not found. Please run data scraper first.")
            return False
        
        chatbot_instance = UniversityAIChatbot()
        logger.info("Chatbot initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")
        return False

# Demo responses for when chatbot is not available
DEMO_RESPONSES = {
    'help': """🎓 **University of Malakand AI Assistant**

I can help you with:
• **Faculty Information** - "Tell me about Dr. [Name]"
• **Departments** - "Information about Computer Science department"
• **Admissions** - "How to apply for admission?"
• **Notifications** - "Latest university news"
• **Research** - "Research papers"
• **General Info** - "About University of Malakand"

**Example Questions:**
- "Who is Dr. Fakhruddin?"
- "How to apply for BS Computer Science?"
- "What are the recent notifications?"

Just ask your question and I'll provide accurate information!""",
    
    'faculty': 'Our university has highly qualified faculty members across various departments. You can ask about specific professors or departments for more information.',
    
    'admission': """**Admission Information:**

The University of Malakand offers various undergraduate and graduate programs.

**Undergraduate Programs:**
- Intermediate (12 years) with relevant subjects
- Entry test (if required)
- Merit-based selection

**Graduate Programs:**
- Bachelor's degree from recognized institution
- Relevant academic background

For specific requirements, visit www.uom.edu.pk""",
    
    'default': "I'm here to help with University of Malakand information. You can ask about faculty, departments, admissions, or general university queries."
}

def get_demo_response(message):
    """Get demo response when chatbot is not available"""
    msg = message.lower()
    
    if 'help' in msg:
        return DEMO_RESPONSES['help']
    elif any(word in msg for word in ['faculty', 'professor', 'teacher']):
        return DEMO_RESPONSES['faculty']
    elif any(word in msg for word in ['admission', 'apply', 'requirement']):
        return DEMO_RESPONSES['admission']
    else:
        return DEMO_RESPONSES['default']

@app.route('/')
def index():
    """Main page with chat interface"""
    return render_template_string(WEB_TEMPLATE)

@app.route('/api/status')
def status():
    """API endpoint to check server status"""
    if chatbot_instance:
        return jsonify({
            'status': 'ready',
            'message': 'AI Assistant Ready!',
            'chatbot_available': True
        })
    else:
        return jsonify({
            'status': 'demo',
            'message': 'Running in Demo Mode',
            'chatbot_available': False
        })

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Log the request
        logger.info(f"Chat request: {message}")
        
        # Get response from chatbot or demo
        if chatbot_instance:
            response = chatbot_instance.chat(message)
        else:
            response = get_demo_response(message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/scrape', methods=['POST'])
def trigger_scraping():
    """API endpoint to trigger data scraping"""
    if not CHATBOT_AVAILABLE:
        return jsonify({'error': 'Scraper not available'}), 400
    
    try:
        # Start scraping in background thread
        def run_scraper():
            scraper = UniversityDataScraper()
            scraper.scrape_university_complete(max_pages=200)
            
            # Reinitialize chatbot after scraping
            global chatbot_instance
            chatbot_instance = UniversityAIChatbot()
        
        scraping_thread = threading.Thread(target=run_scraper)
        scraping_thread.daemon = True
        scraping_thread.start()
        
        return jsonify({
            'message': 'Scraping started in background',
            'status': 'started'
        })
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return jsonify({'error': 'Failed to start scraping'}), 500

@app.route('/api/knowledge-base-info')
def knowledge_base_info():
    """Get information about the knowledge base"""
    data_dir = Path("university_data")
    
    if not data_dir.exists():
        return jsonify({
            'exists': False,
            'message': 'Knowledge base not found'
        })
    
    try:
        # Get file counts
        pages_count = len(list((data_dir / "pages").glob("*.json"))) if (data_dir / "pages").exists() else 0
        faculty_count = len(list((data_dir / "faculty").glob("*.json"))) if (data_dir / "faculty").exists() else 0
        docs_count = len(list((data_dir / "documents").rglob("*"))) if (data_dir / "documents").exists() else 0
        
        return jsonify({
            'exists': True,
            'pages_count': pages_count,
            'faculty_count': faculty_count,
            'documents_count': docs_count,
            'database_exists': (data_dir / "university_knowledge.db").exists()
        })
        
    except Exception as e:
        return jsonify({
            'exists': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🎓 University of Malakand AI Chatbot Server")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot_ready = initialize_chatbot()
    
    if chatbot_ready:
        print("✅ Chatbot initialized successfully!")
    else:
        print("⚠️ Running in demo mode. Run data scraper to enable full functionality.")
    
    print(f"🌐 Starting server...")
    print(f"📱 Access the chatbot at: http://localhost:5000")
    print(f"🔧 API Status: http://localhost:5000/api/status")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',  # Allow external connections (for Codespaces)
        port=5000,
        debug=True,
        threaded=True
    )
