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
            removeTypingIndicator();
            addMessage(data.response || 'Không nhận được phản hồi.', 'bot');
            renderSources(data.sources);
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

    // Render RAG sources (if any)
    function renderSources(sources) {
        const box = document.getElementById('chatSources');
        const list = document.getElementById('chatSourcesList');
        if (!box || !list) return;
        if (!Array.isArray(sources) || sources.length === 0) {
            // Hide if no sources
            box.classList.add('hidden');
            list.innerHTML = '';
            return;
        }
        box.classList.remove('hidden');
        list.innerHTML = '';
        sources.forEach(src => {
            const li = document.createElement('li');
            li.className = 'border border-slate-200 rounded p-2 bg-white';
            const meta = src.meta || {};
            const labelParts = [];
            if (meta.type) labelParts.push(meta.type);
            if (meta.ten_nganh) labelParts.push(meta.ten_nganh);
            if (meta.ma_nganh) labelParts.push(meta.ma_nganh);
            const label = labelParts.join(' • ') || 'Tài liệu';
            const score = typeof src.score === 'number' ? src.score.toFixed(3) : '—';
            const snippet = (src.snippet || '').slice(0, 280);
            li.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="font-medium text-sky-700">${label}</span>
                    <span class="text-[10px] text-slate-500">score: ${score}</span>
                </div>
                <div class="mt-1 text-slate-600 leading-snug text-[11px]">${escapeHtml(snippet)}${snippet.length >= 280 ? '…' : ''}</div>
                <button class="mt-1 text-[10px] text-sky-600 hover:underline toggle-src">Mở rộng</button>
                <pre class="mt-1 hidden whitespace-pre-wrap text-[10px] bg-slate-50 p-1 rounded border border-slate-100 full-snippet">${escapeHtml(src.snippet || '')}</pre>
            `;
            const btn = li.querySelector('.toggle-src');
            const full = li.querySelector('.full-snippet');
            btn.addEventListener('click', () => {
                full.classList.toggle('hidden');
                btn.textContent = full.classList.contains('hidden') ? 'Mở rộng' : 'Thu gọn';
            });
            list.appendChild(li);
        });
    }

    function escapeHtml(str) {
        return str.replace(/[&<>"']/g, function(ch) {
            return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[ch]);
        });
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