// Ombee AI Main App

// Global state
let currentUser = null;
let currentSessionId = null;
let chatSessions = [];

// ===== INITIALIZATION =====
async function initApp() {
    // Check authentication
    const { data: { session } } = await window.OmbeeConfig.supabase.auth.getSession();
    
    if (!session) {
        window.location.href = 'login.html';
        return;
    }
    
    currentUser = session.user;
    
    // Update UI with user info
    const userName = currentUser.user_metadata?.name || currentUser.email.split('@')[0];
    document.getElementById('userName').textContent = userName;
    document.getElementById('userEmail').textContent = currentUser.email;
    document.getElementById('userAvatar').textContent = userName[0].toUpperCase();
    
    loadSidebarState();
    
    await loadChatHistory();
    
    loadTheme();
    
    setupTextareaAutoResize();
    
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session');
    
    if (sessionId) {
        await loadSession(sessionId);
    } else {
        showWelcomeScreen();
    }
}

// Setup textarea auto-resize
function setupTextareaAutoResize() {
    const textarea = document.getElementById('messageInput');
    
    const resize = () => {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    };
    
    textarea.addEventListener('input', resize);
    textarea.addEventListener('keydown', handleKeyPress);
}

// Show welcome without creating session
function showWelcomeScreen() {
    document.getElementById('messages').innerHTML = `
        <div class="welcome-message">
            <h2>Welcome to Ombee AI! 👋</h2>
            <p>Ask me anything about wellness, nutrition, and holistic health.</p>
        </div>
    `;
    currentSessionId = null;
}

// ===== CHAT FUNCTIONS =====
async function createNewChat() {
    try {
        const response = await fetch(`${window.OmbeeConfig.API_URL}/api/sessions/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUser.id })
        });
        
        const data = await response.json();
        currentSessionId = data.session_id;
        
        // Clear messages
        showWelcomeScreen();
        
        // Update URL
        window.history.pushState({}, '', `?session=${currentSessionId}`);
        
        // Reload chat history
        await loadChatHistory();
    } catch (error) {
        console.error('Failed to create chat:', error);
    }
}

async function loadSession(sessionId) {
    try {
        currentSessionId = sessionId;
        
        // Load messages
        const response = await fetch(`${window.OmbeeConfig.API_URL}/api/sessions/${sessionId}/messages`);
        
        if (!response.ok) {
            console.error('Failed to load messages:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error details:', errorText);
            
            // Show error to user
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: red;">
                    Failed to load conversation. Please try again.
                </div>
            `;
            return;
        }
        
        const messages = await response.json();
        
        if (!Array.isArray(messages)) {
            console.error('Messages is not an array:', messages);
            return;
        }
        
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = '';
        
        if (messages.length === 0) {
            messagesDiv.innerHTML = `
                <div class="welcome-message">
                    <h2>Welcome back! 👋</h2>
                    <p>Continue your conversation or ask something new.</p>
                </div>
            `;
        } else {
            messages.forEach(msg => {
                addMessageToUI(msg.content, msg.role, msg.domain, null, msg.sources);
            });
        }
        
        // Update active chat in sidebar
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.toggle('active', item.dataset.sessionId === sessionId);
        });
        
        // Update URL
        window.history.pushState({}, '', `?session=${sessionId}`);
    } catch (error) {
        console.error('Failed to load session:', error);
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${window.OmbeeConfig.API_URL}/api/sessions/list?user_id=${currentUser.id}`);
        const allSessions = await response.json();
        
        // Filter out empty sessions (sessions with 0 messages)
        chatSessions = allSessions.filter(session => session.message_count > 0);
        
        const historyDiv = document.getElementById('chatHistory');
        
        if (chatSessions.length === 0) {
            historyDiv.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No chats yet. Start a new conversation!
                </div>
            `;
            return;
        }
        
        historyDiv.innerHTML = chatSessions.map(session => `
            <div class="chat-item ${session.session_id === currentSessionId ? 'active' : ''}" 
                 data-session-id="${session.session_id}"
                 onclick="loadSession('${session.session_id}')">
                <div class="chat-item-title">${session.title || 'New conversation'}</div>
                <div class="chat-item-meta">
                    ${formatDate(session.updated_at)} • ${session.message_count} messages
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Create session on first message if none exists
    if (!currentSessionId) {
        await createNewChat();
    }
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    
    // Hide welcome message
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();
    
    // Add user message to UI
    addMessageToUI(message, 'user');
    
    // Show typing indicator
    document.getElementById('typingIndicator').classList.add('active');
    document.getElementById('sendButton').disabled = true;
    
    try {
        const response = await fetch(`${window.OmbeeConfig.API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId,
                user_id: currentUser.id
            })
        });
        
        const data = await response.json();
        
        // Update session ID if new
        if (!currentSessionId) {
            currentSessionId = data.session_id;
            window.history.pushState({}, '', `?session=${currentSessionId}`);
        }
        
        // Add AI response
        addMessageToUI(
            data.response,
            'assistant',
            data.domain,
            data.confidence,
            data.sources,
            data.status
        );
        
        // Reload chat history to show updated session
        await loadChatHistory();
    } catch (error) {
        console.error('Error:', error);
        addMessageToUI(
            'Sorry, I encountered an error. Please try again.',
            'assistant'
        );
    } finally {
        document.getElementById('typingIndicator').classList.remove('active');
        document.getElementById('sendButton').disabled = false;
        input.focus();
    }
}

function addMessageToUI(content, role, domain = null, confidence = null, sources = null, status = null) {
    const messagesDiv = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = 'message-wrapper';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format text (basic markdown)
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    contentDiv.innerHTML = formattedContent;
    
    wrapperDiv.appendChild(contentDiv);
    
    // Add details toggle for assistant messages with metadata
    if (role === 'assistant' && (domain || sources)) {
        const toggleId = `details-${Date.now()}`;
        
        const toggleDiv = document.createElement('div');
        toggleDiv.className = 'details-toggle';
        toggleDiv.onclick = () => toggleDetails(toggleId);
        toggleDiv.innerHTML = `
            <span class="arrow">▼</span>
            <span>Show details</span>
        `;
        
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'message-details';
        detailsDiv.id = toggleId;
        
        let detailsHTML = '';
        
        if (domain) {
            const domainIcons = {
                'holistic': '💚',
                'financial': '💰',
                'telecom': '📱'
            };
            detailsHTML += `
                <div class="detail-row">
                    <span class="detail-label">Domain</span>
                    <span class="detail-value">
                        <span class="domain-badge">${domainIcons[domain] || '🔍'} ${domain.toUpperCase()}</span>
                    </span>
                </div>
            `;
        }
        
        if (confidence) {
            detailsHTML += `
                <div class="detail-row">
                    <span class="detail-label">Confidence</span>
                    <span class="detail-value">${Math.round(confidence * 100)}%</span>
                </div>
            `;
        }
        
        if (status) {
            const statusIcons = {
                'live': '✅',
                'demo': '🎭',
                'coming-soon': '🔄',
                'error': '❌'
            };
            detailsHTML += `
                <div class="detail-row">
                    <span class="detail-label">Status</span>
                    <span class="detail-value">${statusIcons[status] || ''} ${status}</span>
                </div>
            `;
        }
        
        if (sources && sources.length > 0) {
            detailsHTML += `
                <div class="detail-row">
                    <span class="detail-label">Sources (${sources.length})</span>
                    <div>
                        <ul class="sources-list">
                            ${sources.map(src => `<li class="source-item">${src}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }
        
        detailsDiv.innerHTML = detailsHTML;
        
        wrapperDiv.appendChild(toggleDiv);
        wrapperDiv.appendChild(detailsDiv);
    }
    
    messageDiv.appendChild(wrapperDiv);
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function toggleDetails(id) {
    const details = document.getElementById(id);
    const toggle = details.previousElementSibling;
    
    if (details.classList.contains('visible')) {
        details.classList.remove('visible');
        toggle.classList.remove('expanded');
    } else {
        details.classList.add('visible');
        toggle.classList.add('expanded');
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ===== SIDEBAR FUNCTIONS =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    
    sidebar.classList.toggle('collapsed');
    
    closeSidebarPopup();
    
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
}

function loadSidebarState() {
    const collapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    const sidebar = document.getElementById('sidebar');
    
    if (collapsed) {
        sidebar.classList.add('collapsed');
    }
}

// ===== SIDEBAR ACTION POPUP FUNCTIONS =====
function toggleSidebarPopup(event) {
    const popup = document.getElementById('sidebarPopup');
    
    event.stopPropagation(); 
    
    if (popup.classList.contains('visible')) {
        closeSidebarPopup();
    } else {
        document.querySelectorAll('.sidebar-popup-actions').forEach(p => p.classList.remove('visible'));
        popup.classList.add('visible');
        document.addEventListener('click', closeSidebarPopup);
    }
}

function closeSidebarPopup() {
    const popup = document.getElementById('sidebarPopup');
    popup.classList.remove('visible');
    document.removeEventListener('click', closeSidebarPopup);
}

// ===== SETTINGS FUNCTIONS =====
async function showSettings() {
    document.getElementById('settingsModal').classList.remove('hidden');
    
    // Load user stats
    try {
        const response = await fetch(`${window.OmbeeConfig.API_URL}/api/stats/${currentUser.id}`);
        const stats = await response.json();
        
        document.getElementById('statSessions').textContent = stats.total_sessions;
        document.getElementById('statMessages').textContent = stats.total_messages;
        document.getElementById('statQueries').textContent = stats.total_queries;
        document.getElementById('statAvgTime').textContent = stats.avg_response_time 
            ? `${stats.avg_response_time.toFixed(2)}s`
            : 'N/A';
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
    
    // Load user preferences
    try {
        const response = await fetch(`${window.OmbeeConfig.API_URL}/api/users/${currentUser.id}`);
        const user = await response.json();
        
        const prefs = user.preferences || {};
        document.getElementById('dietaryRestrictions').value = prefs.dietary_restrictions || '';
        document.getElementById('healthGoals').value = prefs.health_goals || '';
    } catch (error) {
        console.error('Failed to load preferences:', error);
    }
}

function closeSettings() {
    document.getElementById('settingsModal').classList.add('hidden');
}

async function saveSettings() {
    const preferences = {
        dietary_restrictions: document.getElementById('dietaryRestrictions').value,
        health_goals: document.getElementById('healthGoals').value
    };
    
    try {
        await fetch(`${window.OmbeeConfig.API_URL}/api/users/${currentUser.id}/preferences`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ preferences })
        });
        
        alert('Preferences saved!');
        closeSettings();
    } catch (error) {
        console.error('Failed to save preferences:', error);
        alert('Failed to save preferences');
    }
}

async function clearAllChats() {
    if (!confirm('Are you sure you want to delete all chats? This cannot be undone.')) {
        return;
    }
    
    try {
        // Delete all sessions
        for (const session of chatSessions) {
            await fetch(`${window.OmbeeConfig.API_URL}/api/sessions/${session.session_id}`, {
                method: 'DELETE'
            });
        }
        
        alert('All chats deleted');
        closeSettings();
        await createNewChat();
    } catch (error) {
        console.error('Failed to clear chats:', error);
        alert('Failed to clear chats');
    }
}

// ===== THEME FUNCTIONS =====
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update toggle checkbox if in settings
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.checked = newTheme === 'dark';
    }
    
    // Update theme button icon
    const themeBtn = document.querySelector('.theme-toggle');
    if (themeBtn) {
        themeBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeBtn = document.querySelector('.theme-toggle');
    if (themeBtn) {
        themeBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
    
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.checked = savedTheme === 'dark';
    }
}

// ===== LOGOUT =====
async function handleLogout() {
    if (!confirm('Are you sure you want to logout?')) {
        return;
    }
    
    try {
        await window.OmbeeConfig.supabase.auth.signOut();
        window.location.href = 'login.html';
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// ===== UTILITY FUNCTIONS =====
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

// ===== INITIALIZE APP =====
document.addEventListener('DOMContentLoaded', initApp);