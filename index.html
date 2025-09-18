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

        // Simple in-memory chat system (replace with actual backend)
        const chatBot = {
            responses: {
                'hello': 'Hello! Welcome to University of Malakand. How can I help you today?',
                'hi': 'Hi there! I\'m here to help you with any questions about the university.',
                'help': `🎓 **University of Malakand AI Assistant**

I can help you with:
• **Faculty Information** - "Tell me about Dr. [Name]" or "Who teaches [subject]?"
• **Departments** - "Information about Computer Science department"
• **Admissions** - "How to apply for admission?" or "Admission requirements"
• **Notifications** - "Latest university news" or "Recent announcements"
• **Research** - "Research papers" or "Publications"
• **General Info** - "About University of Malakand"

**Example Questions:**
- "Who is Dr. Fakhruddin?"
- "How to apply for BS Computer Science?"
- "What are the recent notifications?"
- "Tell me about the English department"

Just ask your question and I'll provide accurate information!`,
                
                'faculty': 'Our university has highly qualified faculty members across various departments. You can ask about specific professors like "Tell me about Dr. [Name]" or ask about faculty in a particular department.',
                
                'admission': `**Admission Information:**

The University of Malakand offers various undergraduate and graduate programs. Here are the general requirements:

**Undergraduate Programs:**
- Intermediate (12 years) with relevant subjects
- Entry test (if required)
- Merit-based selection

**Graduate Programs:**
- Bachelor's degree from recognized institution
- Relevant academic background
- Entry test and interview

For specific program requirements and deadlines, please visit the university's official admissions page.`,

                'departments': `**Major Departments at University of Malakand:**

• Computer Science & IT
• English Literature
• Mathematics
• Physics
• Chemistry
• Botany
• Zoology
• Economics
• Psychology
• Education

You can ask about specific departments for more detailed information.`,

                'notifications': `**Recent University Updates:**

For the most current notifications and announcements, please check:
• University website: www.uom.edu.pk
• Official notice boards
• Department announcements

You can ask me about specific types of notifications like "exam schedules" or "admission dates".`,

                'default': 'I understand you\'re asking about the university. While I\'m still learning, I can help with information about faculty, departments, admissions, and general university queries. Could you please rephrase your question or be more specific?'
            },

            getResponse(message) {
                const msg = message.toLowerCase().trim();
                
                // Simple keyword matching (replace with actual AI processing)
                if (msg.includes('hello') || msg.includes('hi')) return this.responses.hello;
                if (msg.includes('help')) return this.responses.help;
                if (msg.includes('faculty') || msg.includes('professor') || msg.includes('teacher')) return this.responses.faculty;
                if (msg.includes('admission') || msg.includes('apply')) return this.responses.admission;
                if (msg.includes('department') || msg.includes('dept')) return this.responses.departments;
                if (msg.includes('notification') || msg.includes('news') || msg.includes('announcement')) return this.responses.notifications;
                
                // Check for specific faculty names
                if (msg.includes('dr.') || msg.includes('prof')) {
                    return 'I can help you find information about faculty members. However, my knowledge base is currently being built. For specific faculty information, you can check the university website or provide more details about which department they belong to.';
                }
                
                return this.responses.default;
            }
        };

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

        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, true);
            messageInput.value = '';

            // Show typing indicator
            showTyping();

            // Simulate processing delay
            setTimeout(() => {
                hideTyping();
                const response = chatBot.getResponse(message);
                addMessage(response);
            }, 1000 + Math.random() * 1000); // Random delay 1-2 seconds
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

        // Show connection status
        window.addEventListener('load', () => {
            showStatus('AI Assistant Ready!', 'success');
        });
    </script>
</body>
</html>
