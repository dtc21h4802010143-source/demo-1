// Floating Chat Widget
class FloatingChatWidget {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createWidget();
        this.attachEventListeners();
        this.loadChatHistory();
    }

    createWidget() {
        const widgetHTML = `
            <div class="floating-chat-widget" id="floatingChat">
                <!-- Toggle Button -->
                <button class="chat-toggle-btn" id="chatToggleBtn" aria-label="Mở chat">
                    <i class="fas fa-comments"></i>
                    <span class="badge" style="display: none;">0</span>
                </button>

                <!-- Chat Window -->
                <div class="chat-window-popup" id="chatWindowPopup">
                    <!-- Header -->
                    <div class="chat-header">
                        <div class="chat-header-info">
                            <div class="chat-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="chat-header-text">
                                <h3>Trợ Lý AI Tuyển Sinh</h3>
                                <p><i class="fas fa-circle" style="font-size: 8px; color: #10b981;"></i> Đang hoạt động</p>
                            </div>
                        </div>
                        <button class="chat-close-btn" id="chatCloseBtn" aria-label="Đóng chat">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <!-- Quick Actions -->
                    <div class="quick-actions" id="quickActions">
                        <button class="quick-action-btn" data-message="Điểm chuẩn các ngành năm nay là bao nhiêu?">
                            <i class="fas fa-chart-line"></i> Điểm chuẩn
                        </button>
                        <button class="quick-action-btn" data-message="Tư vấn ngành học phù hợp với điểm của tôi">
                            <i class="fas fa-graduation-cap"></i> Tư vấn ngành
                        </button>
                        <button class="quick-action-btn" data-message="Hướng dẫn nộp hồ sơ tuyển sinh">
                            <i class="fas fa-file-alt"></i> Nộp hồ sơ
                        </button>
                        <button class="quick-action-btn" data-message="Lịch tuyển sinh năm 2025">
                            <i class="fas fa-calendar-alt"></i> Lịch tuyển sinh
                        </button>
                        <button class="quick-action-btn" data-message="Học phí các ngành là bao nhiêu?">
                            <i class="fas fa-money-bill-wave"></i> Học phí
                        </button>
                    </div>

                    <!-- Messages Area -->
                    <div class="chat-messages-area" id="chatMessagesArea">
                        <!-- Welcome Message -->
                        <div class="welcome-message" id="welcomeMessage">
                            <i class="fas fa-robot"></i>
                            <h4>Xin chào! 👋</h4>
                            <p>Tôi là trợ lý AI tuyển sinh. Tôi có thể giúp gì cho bạn?</p>
                            <div class="welcome-suggestions">
                                <button class="welcome-suggestion-btn" data-message="Tôi muốn tư vấn ngành học phù hợp">
                                    <i class="fas fa-lightbulb"></i>
                                    <span>Tư vấn ngành học phù hợp với điểm số của tôi</span>
                                </button>
                                <button class="welcome-suggestion-btn" data-message="Xem điểm chuẩn các năm trước">
                                    <i class="fas fa-chart-bar"></i>
                                    <span>Xem điểm chuẩn các năm trước</span>
                                </button>
                                <button class="welcome-suggestion-btn" data-message="Hướng dẫn đăng ký xét tuyển">
                                    <i class="fas fa-question-circle"></i>
                                    <span>Hướng dẫn đăng ký xét tuyển online</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Input Area -->
                    <div class="chat-input-area">
                        <div class="chat-input-wrapper">
                            <input 
                                type="text" 
                                class="chat-input-field" 
                                id="chatInputField" 
                                placeholder="Nhập câu hỏi của bạn..."
                                autocomplete="off"
                            >
                            <button class="chat-send-btn" id="chatSendBtn" aria-label="Gửi tin nhắn">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Powered By -->
                    <div class="chat-powered-by">
                        Powered by <i class="fas fa-brain"></i> AI Technology
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('chatToggleBtn');
        const closeBtn = document.getElementById('chatCloseBtn');
        const sendBtn = document.getElementById('chatSendBtn');
        const inputField = document.getElementById('chatInputField');
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        const welcomeSuggestionBtns = document.querySelectorAll('.welcome-suggestion-btn');

        // Toggle chat window
        toggleBtn?.addEventListener('click', () => this.toggleChat());
        closeBtn?.addEventListener('click', () => this.closeChat());

        // Send message
        sendBtn?.addEventListener('click', () => this.sendMessage());
        inputField?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Quick actions
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.sendMessage(message);
            });
        });

        // Welcome suggestions
        welcomeSuggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.sendMessage(message);
            });
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });
    }

    toggleChat() {
        const chatWindow = document.getElementById('chatWindowPopup');
        const toggleBtn = document.getElementById('chatToggleBtn');
        
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            chatWindow.classList.add('active');
            toggleBtn.style.display = 'none';
            document.getElementById('chatInputField')?.focus();
            this.clearBadge();
        } else {
            chatWindow.classList.remove('active');
            toggleBtn.style.display = 'flex';
        }
    }

    closeChat() {
        const chatWindow = document.getElementById('chatWindowPopup');
        const toggleBtn = document.getElementById('chatToggleBtn');
        
        this.isOpen = false;
        chatWindow.classList.remove('active');
        toggleBtn.style.display = 'flex';
    }

    async sendMessage(messageText = null) {
        const inputField = document.getElementById('chatInputField');
        const message = messageText || inputField.value.trim();

        if (!message) return;

        // Hide welcome message
        const welcomeMsg = document.getElementById('welcomeMessage');
        if (welcomeMsg) welcomeMsg.style.display = 'none';

        // Add user message
        this.addMessage(message, 'user');

        // Clear input
        if (!messageText) inputField.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Remove typing indicator
            this.removeTypingIndicator();

            // Add bot response
            if (data.response) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.', 'bot');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.removeTypingIndicator();
            this.addMessage('Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.', 'bot');
        }

        // Save to history
        this.saveChatHistory();
    }

    addMessage(text, sender) {
        const messagesArea = document.getElementById('chatMessagesArea');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'chat-message-avatar';
        avatarDiv.innerHTML = sender === 'bot' 
            ? '<i class="fas fa-robot"></i>' 
            : '<i class="fas fa-user"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'chat-message-content';
        contentDiv.textContent = text;

        const timeSpan = document.createElement('span');
        timeSpan.className = 'chat-message-time';
        timeSpan.textContent = this.getCurrentTime();

        const contentWrapper = document.createElement('div');
        contentWrapper.appendChild(contentDiv);
        contentWrapper.appendChild(timeSpan);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentWrapper);

        messagesArea.appendChild(messageDiv);
        this.scrollToBottom();

        // Store message
        this.messages.push({ text, sender, time: new Date().toISOString() });
    }

    showTypingIndicator() {
        const messagesArea = document.getElementById('chatMessagesArea');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator-wrapper';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="chat-message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        messagesArea.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    scrollToBottom() {
        const messagesArea = document.getElementById('chatMessagesArea');
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    updateBadge(count) {
        const badge = document.querySelector('.chat-toggle-btn .badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 9 ? '9+' : count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    clearBadge() {
        this.updateBadge(0);
    }

    saveChatHistory() {
        try {
            localStorage.setItem('chatHistory', JSON.stringify(this.messages));
        } catch (e) {
            console.error('Failed to save chat history:', e);
        }
    }

    loadChatHistory() {
        try {
            const history = localStorage.getItem('chatHistory');
            if (history) {
                this.messages = JSON.parse(history);
                // Optionally restore last few messages
                // this.messages.slice(-5).forEach(msg => {
                //     this.addMessage(msg.text, msg.sender);
                // });
            }
        } catch (e) {
            console.error('Failed to load chat history:', e);
        }
    }
}

// Initialize floating chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new FloatingChatWidget();
});
