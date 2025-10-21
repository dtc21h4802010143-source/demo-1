document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendMessage');
    const suggestionChips = document.querySelectorAll('.chip');

    // Handle user input
    function handleUserInput(message) {
        if (!message.trim()) return;

        // Add user message to chat
        addMessage(message, 'user');

        // Show typing indicator
        showTypingIndicator();

        // Send message to backend
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();

            // Add bot response to chat
            addMessage(data.response, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage('Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.', 'bot');
        });

        // Clear input
        userInput.value = '';
    }

    // Add message to chat window
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = message;

        const timeDiv = document.createElement('div');
        timeDiv.classList.add('message-time');
        timeDiv.textContent = getCurrentTime();

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Show typing indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('message', 'bot', 'typing-indicator');
        indicator.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(indicator);
        scrollToBottom();
    }

    // Remove typing indicator
    function removeTypingIndicator() {
        const indicator = chatMessages.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Get current time
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit'
        });
    }

    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners
    sendButton.addEventListener('click', () => {
        handleUserInput(userInput.value);
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleUserInput(userInput.value);
        }
    });

    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            handleUserInput(chip.textContent);
        });
    });

    // Focus input on load
    userInput.focus();

    // Handle file drops for document sharing
    const dropZone = document.querySelector('.chat-window');
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Handle file upload
    function handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addMessage(`Đã tải lên tệp: ${file.name}`, 'user');
                // Wait for bot to process the file
                handleUserInput('Vui lòng xem xét tệp tôi vừa gửi');
            } else {
                addMessage('Không thể tải lên tệp. ' + data.error, 'bot');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Có lỗi xảy ra khi tải lên tệp.', 'bot');
        });
    }

    // Chatbot floating widget logic
    if (document.getElementById('chatbot-toggle')) {
        const chatbotToggle = document.getElementById('chatbot-toggle');
        const chatbotBox = document.getElementById('chatbot-box');
        const chatbotClose = document.getElementById('chatbot-close');
        const chatbotForm = document.getElementById('chatbot-form');
        const chatbotInput = document.getElementById('chatbot-input');
        const chatbotMessages = document.getElementById('chatbot-messages');

        chatbotToggle.onclick = () => {
            chatbotBox.style.display = 'block';
            chatbotToggle.style.display = 'none';
        };
        chatbotClose.onclick = () => {
            chatbotBox.style.display = 'none';
            chatbotToggle.style.display = 'block';
        };

        chatbotForm.onsubmit = async function(e) {
            e.preventDefault();
            const msg = chatbotInput.value.trim();
            if (!msg) return;
            appendMessage('Bạn', msg, 'right');
            chatbotInput.value = '';
            chatbotInput.disabled = true;
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                if (data.response) {
                    appendMessage('Chatbot', data.response, 'left');
                } else {
                    appendMessage('Chatbot', 'Xin lỗi, tôi chưa hiểu câu hỏi này.', 'left');
                }
            } catch {
                appendMessage('Chatbot', 'Lỗi kết nối máy chủ.', 'left');
            }
            chatbotInput.disabled = false;
            chatbotInput.focus();
        };

        function appendMessage(sender, text, align) {
            const msgDiv = document.createElement('div');
            msgDiv.style.textAlign = align;
            msgDiv.innerHTML = `<b>${sender}:</b> ${text}`;
            chatbotMessages.appendChild(msgDiv);
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }
    }
});