class RealtimeAIChat {
    constructor() {
        this.socket = null;
        this.sessionId = null;
        this.userId = null;
        this.isConnected = false;
        this.messageCount = 0;
        this.toolCallCount = 0;
        this.currentAiResponse = '';
        this.isAiTyping = false;
        
        this.init();
    }
    
    init() {
        this.updateUI();
        
        // Generate a session ID if not in URL
        const urlParams = new URLSearchParams(window.location.search);
        this.sessionId = urlParams.get('session_id') || this.generateSessionId();
        
        // Update URL with session ID
        if (!urlParams.get('session_id')) {
            const newUrl = window.location.pathname + '?session_id=' + this.sessionId;
            window.history.replaceState({}, '', newUrl);
        }
        
        document.getElementById('sessionId').textContent = this.sessionId;
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    async connectWebSocket() {
        if (this.isConnected) {
            this.addMessage('Already connected', 'system');
            return;
        }
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
            const wsUrl = `${protocol}//${host}/ws/session/${this.sessionId}`;
            
            this.socket = new WebSocket(wsUrl);
            
            this.updateStatus('connecting');
            this.addMessage('Connecting to server...', 'system');
            
            this.socket.onopen = () => {
                this.isConnected = true;
                this.updateStatus('connected');
                this.addMessage('Connected successfully!', 'system');
                this.updateUI();
                this.updateConnectionTime();
            };
            
            this.socket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.socket.onclose = () => {
                this.isConnected = false;
                this.updateStatus('disconnected');
                this.addMessage('Disconnected from server', 'system');
                this.updateUI();
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addMessage('Connection error occurred', 'system');
            };
            
        } catch (error) {
            console.error('Failed to connect:', error);
            this.addMessage('Failed to connect: ' + error.message, 'system');
            this.updateStatus('disconnected');
            this.updateUI();
        }
    }
    
    disconnectWebSocket() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            this.isConnected = false;
            this.updateStatus('disconnected');
            this.updateUI();
        }
    }
    
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            switch (message.type) {
                case 'system':
                    this.addMessage(message.message, 'system');
                    break;
                    
                case 'session_info':
                    this.userId = message.user_id;
                    document.getElementById('userId').textContent = this.userId;
                    this.addMessage(`Session ID: ${message.session_id}`, 'system');
                    break;
                    
                case 'ai_stream':
                    if (!this.isAiTyping) {
                        this.isAiTyping = true;
                        this.currentAiResponse = '';
                        this.addTypingIndicator();
                    }
                    this.currentAiResponse += message.token;
                    this.updateTypingIndicator(this.currentAiResponse);
                    break;
                    
                case 'ai_stream_end':
                    this.removeTypingIndicator();
                    if (this.currentAiResponse) {
                        this.addMessage(this.currentAiResponse, 'ai');
                        this.messageCount++;
                        this.updateMessageCount();
                    }
                    this.currentAiResponse = '';
                    this.isAiTyping = false;
                    break;
                    
                case 'tool_result':
                    this.toolCallCount++;
                    this.updateToolCallCount();
                    this.addToolResult(message.tool_name, message.result);
                    break;
                    
                case 'error':
                    this.addMessage(`Error: ${message.message}`, 'system');
                    break;
                    
                default:
                    console.log('Unknown message type:', message);
            }
        } catch (error) {
            console.error('Error parsing message:', error, data);
        }
    }
    
    sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message || !this.isConnected || !this.socket) {
            return;
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageCount++;
        this.updateMessageCount();
        
        // Send to server
        this.socket.send(JSON.stringify({
            type: 'user_message',
            message: message
        }));
        
        // Clear input
        input.value = '';
        input.focus();
    }
    
    testToolCall() {
        if (!this.isConnected || !this.socket) {
            this.addMessage('Not connected to server', 'system');
            return;
        }
        
        const testPrompts = [
            "Calculate the square root of 144",
            "Fetch weather data for 3 random cities",
            "Analyze sentiment of: 'I'm really happy with the service but the price could be better'",
            "Generate Python code to reverse a string"
        ];
        
        const randomPrompt = testPrompts[Math.floor(Math.random() * testPrompts.length)];
        
        document.getElementById('messageInput').value = randomPrompt;
        this.sendMessage();
    }
    
    endSession() {
        if (this.socket && this.isConnected) {
            this.socket.send(JSON.stringify({
                type: 'end_session'
            }));
            this.addMessage('Ending session...', 'system');
        }
    }
    
    newSession() {
        // Generate new session ID
        this.sessionId = this.generateSessionId();
        
        // Update URL
        const newUrl = window.location.pathname + '?session_id=' + this.sessionId;
        window.history.pushState({}, '', newUrl);
        
        // Update UI
        document.getElementById('sessionId').textContent = this.sessionId;
        document.getElementById('userId').textContent = 'Not connected';
        
        // Clear chat
        this.clearChat();
        
        // Disconnect if connected
        if (this.isConnected) {
            this.disconnectWebSocket();
        }
        
        this.addMessage('New session created. Click "Connect" to start.', 'system');
    }
    
    async viewSessionData() {
        if (!this.sessionId) {
            alert('No session ID available');
            return;
        }
        
        try {
            const response = await fetch(`/api/session/${this.sessionId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch session data');
            }
            
            const data = await response.json();
            
            // Show in console for now
            console.log('Session Data:', data);
            
            // Create a simple modal to display data
            this.showDataModal(data);
            
        } catch (error) {
            console.error('Error fetching session data:', error);
            alert('Error fetching session data: ' + error.message);
        }
    }
    
    showDataModal(data) {
        // Create modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 90%;
            max-height: 90%;
            overflow: auto;
            width: 600px;
        `;
        
        modalContent.innerHTML = `
            <h2>Session Data</h2>
            <h3>Session Info</h3>
            <pre>${JSON.stringify(data.session, null, 2)}</pre>
            <h3>Events (${data.events.length})</h3>
            <pre>${JSON.stringify(data.events, null, 2)}</pre>
            <div style="margin-top: 20px; text-align: right;">
                <button onclick="this.closest('div[style*=\"position: fixed\"]').remove()" 
                        style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Close
                </button>
            </div>
        `;
        
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    addMessage(text, type) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        
        messageDiv.className = `message ${type}-message`;
        messageDiv.textContent = text;
        
        // Add to chat
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    addToolResult(toolName, result) {
        const chatMessages = document.getElementById('chatMessages');
        const toolDiv = document.createElement('div');
        
        toolDiv.className = 'tool-result';
        toolDiv.innerHTML = `
            <strong>${toolName} Result:</strong>
            <pre>${JSON.stringify(result, null, 2)}</pre>
        `;
        
        // Add to chat
        chatMessages.appendChild(toolDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    addTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span> AI is typing...';
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    updateTypingIndicator(text) {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.innerHTML = `<span></span><span></span><span></span> ${text}`;
        }
    }
    
    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        this.messageCount = 0;
        this.toolCallCount = 0;
        this.updateMessageCount();
        this.updateToolCallCount();
    }
    
    updateStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        const indicator = document.getElementById('statusIndicator');
        
        statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        indicator.className = 'status-indicator ' + status;
    }
    
    updateUI() {
        const connectBtn = document.getElementById('connectBtn');
        const disconnectBtn = document.getElementById('disconnectBtn');
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        const toolBtn = document.getElementById('toolBtn');
        const endSessionBtn = document.getElementById('endSessionBtn');
        const newSessionBtn = document.getElementById('newSessionBtn');
        
        if (this.isConnected) {
            connectBtn.disabled = true;
            disconnectBtn.disabled = false;
            sendBtn.disabled = false;
            messageInput.disabled = false;
            toolBtn.disabled = false;
            endSessionBtn.disabled = false;
            newSessionBtn.disabled = false;
        } else {
            connectBtn.disabled = false;
            disconnectBtn.disabled = true;
            sendBtn.disabled = true;
            messageInput.disabled = true;
            toolBtn.disabled = true;
            endSessionBtn.disabled = true;
            newSessionBtn.disabled = false;
        }
    }
    
    updateMessageCount() {
        document.getElementById('messageCount').textContent = this.messageCount;
    }
    
    updateToolCallCount() {
        document.getElementById('toolCallCount').textContent = this.toolCallCount;
    }
    
    updateConnectionTime() {
        const now = new Date();
        document.getElementById('connectedAt').textContent = now.toLocaleTimeString();
    }
    
    setPrompt(prompt) {
        if (!this.isConnected) {
            alert('Please connect first');
            return;
        }
        
        document.getElementById('messageInput').value = prompt;
        document.getElementById('messageInput').focus();
    }
    
    handleKeyPress(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.sendMessage();
        }
    }
}

// Initialize the application
let chatApp;

document.addEventListener('DOMContentLoaded', () => {
    chatApp = new RealtimeAIChat();
    
    // Make functions available globally for button onclick handlers
    window.connectWebSocket = () => chatApp.connectWebSocket();
    window.disconnectWebSocket = () => chatApp.disconnectWebSocket();
    window.sendMessage = () => chatApp.sendMessage();
    window.handleKeyPress = (e) => chatApp.handleKeyPress(e);
    window.testToolCall = () => chatApp.testToolCall();
    window.endSession = () => chatApp.endSession();
    window.newSession = () => chatApp.newSession();
    window.viewSessionData = () => chatApp.viewSessionData();
    window.setPrompt = (prompt) => chatApp.setPrompt(prompt);
    
    // Add click handlers to example prompts
    document.querySelectorAll('.clickable').forEach(item => {
        item.style.cursor = 'pointer';
        item.style.transition = 'background 0.3s';
        item.addEventListener('mouseenter', () => {
            item.style.background = '#edf2f7';
        });
        item.addEventListener('mouseleave', () => {
            item.style.background = '#f7fafc';
        });
    });
});