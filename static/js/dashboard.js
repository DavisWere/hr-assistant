class HRAssistant {
    constructor() {
        this.messages = [];
        this.isRecording = false;
        this.recognition = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSpeechRecognition();
        this.loadChatHistory();
    }

    setupEventListeners() {
        // Send message
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Voice input
        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceInput());

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());

        // Quick actions
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuickAction(e.target.dataset.topic));
        });

        // Escalation
        document.getElementById('escalateBtn').addEventListener('click', () => this.showEscalationModal());
        document.getElementById('closeModal').addEventListener('click', () => this.hideEscalationModal());
        document.getElementById('cancelEscalation').addEventListener('click', () => this.hideEscalationModal());
        document.getElementById('confirmEscalation').addEventListener('click', () => this.handleEscalation());

        // Modal backdrop click
        document.getElementById('escalationModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.hideEscalationModal();
        });
    }

    setupSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('messageInput').value = transcript;
                this.stopRecording();
            };

            this.recognition.onerror = () => {
                this.stopRecording();
                this.showNotification('Voice recognition error. Please try again.', 'error');
            };

            this.recognition.onend = () => {
                this.stopRecording();
            };
        }
    }

    toggleVoiceInput() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        if (!this.recognition) {
            this.showNotification('Voice recognition not supported in this browser.', 'error');
            return;
        }

        this.isRecording = true;
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        
        this.recognition.start();
        this.showNotification('Listening... Click to stop.', 'info');
    }

    stopRecording() {
        this.isRecording = false;
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Simulate API call
            const response = await this.getAIResponse(message);
            this.hideTypingIndicator();
            this.addMessage(response, 'assistant');
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('I apologize, but I encountered an error. Please try again.', 'assistant');
        }
    }

    async getAIResponse(message) {
        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    message: message
                })
            });
    
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.response;
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
    addMessage(content, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <p>${content}</p>
                <div class="message-time">${currentTime}</div>
                ${sender === 'assistant' ? this.getFeedbackButtons() : ''}
            </div>
        `;

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add to messages array
        this.messages.push({ content, sender, timestamp: new Date() });
        this.saveChatHistory();

        // Setup feedback buttons if assistant message
        if (sender === 'assistant') {
            this.setupFeedbackButtons(messageElement);
        }
    }

    getFeedbackButtons() {
        return `
            <div class="feedback-buttons">
                <button class="feedback-btn" data-feedback="positive">
                    <i class="fas fa-thumbs-up"></i>
                </button>
                <button class="feedback-btn" data-feedback="negative">
                    <i class="fas fa-thumbs-down"></i>
                </button>
            </div>
        `;
    }

    setupFeedbackButtons(messageElement) {
        const feedbackButtons = messageElement.querySelectorAll('.feedback-btn');
        feedbackButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const feedback = e.target.closest('.feedback-btn').dataset.feedback;
                this.handleFeedback(feedback, messageElement);
            });
        });
    }
 
    handleFeedback(feedback, messageElement) {
        // Mark button as selected
        const buttons = messageElement.querySelectorAll('.feedback-btn');
        buttons.forEach(btn => btn.classList.remove('selected'));
        
        const selectedBtn = messageElement.querySelector(`[data-feedback="${feedback}"]`);
        selectedBtn.classList.add('selected');
 
        // Store feedback
        this.storeFeedback(feedback);
        
        // Show thank you message
        this.showNotification('Thank you for your feedback!', 'success');
    }
 
    storeFeedback(feedback) {
        const feedbackData = {
            feedback,
            timestamp: new Date(),
            messageIndex: this.messages.length - 1
        };
        
        let storedFeedback = JSON.parse(localStorage.getItem('hr_assistant_feedback') || '[]');
        storedFeedback.push(feedbackData);
        localStorage.setItem('hr_assistant_feedback', JSON.stringify(storedFeedback));
    }
 
    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingElement = document.createElement('div');
        typingElement.className = 'message assistant-message typing-indicator';
        typingElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
 
    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
 
    handleQuickAction(topic) {
        const topicMessages = {
            'company-policies': 'Tell me about company policies',
            'conflict-resolution': 'I need help with conflict resolution',
            'stress-management': 'I\'m looking for stress management resources',
            'career-growth': 'I want to discuss career growth opportunities'
        };
 
        const message = topicMessages[topic];
        if (message) {
            document.getElementById('messageInput').value = message;
            this.sendMessage();
        }
    }
 
    showEscalationModal() {
        const modal = document.getElementById('escalationModal');
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
 
    hideEscalationModal() {
        const modal = document.getElementById('escalationModal');
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
 
    async handleEscalation() {
        const textarea = document.querySelector('#escalationModal textarea');
        const details = textarea.value.trim();
        
        if (!details) {
            this.showNotification('Please provide details about your issue.', 'error');
            return;
        }
 
        try {
            // Simulate API call to escalate
            await this.escalateToHuman(details);
            this.hideEscalationModal();
            this.showNotification('Your issue has been forwarded to HR. You will receive a response within 24 hours.', 'success');
            textarea.value = '';
        } catch (error) {
            this.showNotification('Failed to escalate your request. Please try again.', 'error');
        }
    }
 
    async escalateToHuman(details) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Store escalation data
        const escalationData = {
            details,
            timestamp: new Date(),
            chatHistory: this.messages.slice(-10) // Last 10 messages for context
        };
        
        let escalations = JSON.parse(localStorage.getItem('hr_escalations') || '[]');
        escalations.push(escalationData);
        localStorage.setItem('hr_escalations', JSON.stringify(escalations));
        
        // In real implementation, this would send to backend
        console.log('Escalation sent:', escalationData);
    }
 
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('hr_assistant_theme', newTheme);
        
        const themeIcon = document.querySelector('#themeToggle i');
        themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
 
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
 
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
 
    saveChatHistory() {
        localStorage.setItem('hr_assistant_messages', JSON.stringify(this.messages));
    }
 
    loadChatHistory() {
        const savedMessages = localStorage.getItem('hr_assistant_messages');
        if (savedMessages) {
            this.messages = JSON.parse(savedMessages);
            // Optionally restore last few messages to chat
            this.messages.slice(-5).forEach(msg => {
                if (msg.sender !== 'assistant' || this.messages.indexOf(msg) === this.messages.length - 1) {
                    // Don't restore old assistant messages except the last one
                    this.addMessageToUI(msg.content, msg.sender);
                }
            });
        }
        
        // Load theme
        const savedTheme = localStorage.getItem('hr_assistant_theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
            const themeIcon = document.querySelector('#themeToggle i');
            themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
 
    addMessageToUI(content, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <p>${content}</p>
                <div class="message-time">Previous session</div>
            </div>
        `;
 
        chatMessages.appendChild(messageElement);
    }
 
    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="message assistant-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <p>Hi! I'm your AI HR Assistant. How can I help you today?</p>
                    <div class="message-time">Just now</div>
                </div>
            </div>
        `;
        this.messages = [];
        this.saveChatHistory();
    }
 
    exportChat() {
        const chatData = {
            messages: this.messages,
            exportDate: new Date(),
            user: 'Current User'
        };
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `hr-chat-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
 }
 
 // Additional CSS for notifications and typing indicator
 const additionalStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success { background: var(--success-color); }
    .notification-error { background: var(--error-color); }
    .notification-warning { background: var(--warning-color); }
    .notification-info { background: var(--primary-color); }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .typing-indicator .message-content {
        padding: 1rem;
    }
    
    .typing-dots {
        display: flex;
        gap: 0.25rem;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--text-secondary);
        animation: typing 1.4s infinite;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% { opacity: 0.3; }
        30% { opacity: 1; }
    }
 `;
 
 // Inject additional styles
 const styleSheet = document.createElement('style');
 styleSheet.textContent = additionalStyles;
 document.head.appendChild(styleSheet);
 
 // Initialize the application
 document.addEventListener('DOMContentLoaded', () => {
    new HRAssistant();
 });