/**
 * FirstAid AI - Interactive Decision-Tree Chatbot System
 */

let currentConversationId = null;

document.addEventListener('DOMContentLoaded', () => {
    initChatbot();
});

function initChatbot() {
    const fab = document.getElementById('chatbotFab');
    const drawer = document.getElementById('chatbotDrawer');
    const closeBtn = document.getElementById('chatCloseBtn');
    const sendBtn = document.getElementById('chatSendBtn');
    const input = document.getElementById('chatInput');

    if (!fab || !drawer) return;

    fab.addEventListener('click', () => {
        drawer.classList.toggle('open');
        if (drawer.classList.contains('open') && input) {
            input.focus();
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            drawer.classList.remove('open');
        });
    }

    if (sendBtn && input) {
        sendBtn.addEventListener('click', () => handleUserSend());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleUserSend();
        });
    }

    // Global listener for chip buttons and decision tree quick reply buttons
    document.addEventListener('click', (e) => {
        // Quick suggestion chips or decision tree option buttons
        const optionBtn = e.target.closest('.tree-option-btn, .chip-btn');
        if (optionBtn) {
            const promptText = optionBtn.getAttribute('data-value') || optionBtn.textContent.trim();
            
            // Disable sibling option buttons in the same container to prevent multiple clicks
            const container = optionBtn.closest('.chat-suggestions, .tree-options-container');
            if (container) {
                const btns = container.querySelectorAll('.tree-option-btn, .chip-btn');
                btns.forEach(b => {
                    b.disabled = true;
                    b.style.opacity = '0.6';
                    b.style.pointerEvents = 'none';
                });
            }

            if (promptText === "Start Again / Reset" || promptText === "Ask About Another Emergency") {
                resetChatbotState();
                return;
            }

            handleUserSend(promptText);
            return;
        }
    });
}

function handleUserSend(overrideText = null) {
    const input = document.getElementById('chatInput');
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;

    const query = overrideText ? overrideText : (input ? input.value.trim() : '');
    if (!query) return;

    // Append user message to chat UI
    appendChatMessage(query, 'user');
    if (input && !overrideText) input.value = '';

    // Show loading bot message
    const loadingId = 'loading-' + Date.now();
    appendChatMessage('Analyzing situation...', 'bot', loadingId);

    // Call decision tree backend API endpoint
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query, conversation_id: currentConversationId })
    })
    .then(res => res.json())
    .then(data => {
        removeChatMessage(loadingId);

        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
        }

        if (data.is_complete) {
            renderDecisionTreeResult(data);
        } else if (data.options && data.options.length > 0) {
            renderDecisionTreeQuestion(data);
        } else if (data.message) {
            appendChatMessage(data.message, 'bot');
        } else {
            appendChatMessage("I want to make sure I understand correctly. Can you describe what happened or select one of the common first-aid topics?", 'bot');
        }
    })
    .catch(err => {
        removeChatMessage(loadingId);
        appendChatMessage("Sorry, an error occurred while connecting to the assistant. Please try again or call emergency services (112) immediately if urgent.", 'bot');
    });
}

function renderDecisionTreeQuestion(data) {
    const optionsHtml = (data.options || []).map(opt => `
        <button class="tree-option-btn chip-btn" data-value="${escapeHtml(opt)}" style="margin: 0.2rem 0; width: 100%; text-align: left; justify-content: flex-start; padding: 0.5rem 0.75rem; border-radius: 6px; font-weight: 500;">
            🔹 ${escapeHtml(opt)}
        </button>
    `).join('');

    const botHtml = `
        <div class="tree-question-box" style="margin: 0.2rem 0;">
            <p style="margin: 0 0 0.5rem 0; font-weight: 600; color: var(--text-main, #1e293b); line-height: 1.4;">${escapeHtml(data.message)}</p>
            <div class="tree-options-container" style="display: flex; flex-direction: column; gap: 0.3rem;">
                ${optionsHtml}
            </div>
        </div>
    `;

    appendChatMessage(botHtml, 'bot', null, true);
}

function renderDecisionTreeResult(data) {
    const isEmergency = data.emergency || data.urgency === 'EMERGENCY';
    const isUrgent = data.urgency === 'URGENT';
    
    let headerColor = '#0f172a';
    let cardBg = '#f8fafc';
    let borderColor = '#e2e8f0';

    if (isEmergency) {
        headerColor = '#991b1b';
        cardBg = '#fff1f2';
        borderColor = '#fca5a5';
    } else if (isUrgent) {
        headerColor = '#9a3412';
        cardBg = '#fff7ed';
        borderColor = '#fdba74';
    }

    const guidanceSteps = (data.guidance || []).map((step, idx) => `
        <li style="margin-bottom: 0.45rem; line-height: 1.4;">
            <strong style="color: #1e293b;">${idx + 1}.</strong> ${escapeHtml(step)}
        </li>
    `).join('');

    const botHtml = `
        <div class="tree-result-card" style="margin: 0.4rem 0; padding: 0.85rem; border-radius: 8px; background: ${cardBg}; border: 1px solid ${borderColor};">
            
            ${isEmergency ? `
                <div class="qa-red-banner" style="background:#dc2626; color:white; padding:0.65rem 0.85rem; border-radius:6px; margin-bottom:0.75rem; display:flex; align-items:center; gap:0.5rem;">
                    <span style="font-size:1.4rem;">🚨</span>
                    <div>
                        <strong style="display:block; font-size:0.92rem;">⚠️ EMERGENCY MEDICAL WARNING</strong>
                        <span style="font-size:0.78rem;">Please call emergency services (112) immediately!</span>
                    </div>
                    <a href="tel:112" class="btn-emergency-call" style="margin-left:auto; padding:0.35rem 0.65rem; font-size:0.78rem; background:white; color:#dc2626; border-radius:4px; text-decoration:none; font-weight:700;">
                        📞 Call 112
                    </a>
                </div>
            ` : ''}

            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <h4 style="margin:0; font-size:0.98rem; color:${headerColor}; font-weight:700;">${escapeHtml(data.title || 'First-Aid Guidance')}</h4>
                <span class="severity-badge ${(data.urgency || 'low').toLowerCase()}" style="font-size:0.72rem; padding:0.15rem 0.45rem; border-radius:4px; font-weight:700;">${escapeHtml(data.urgency || 'LOW')}</span>
            </div>

            ${data.warning ? `
                <div style="font-size:0.84rem; padding:0.5rem; background:${isEmergency ? '#fee2e2' : (isUrgent ? '#ffedd5' : '#f1f5f9')}; border-left:3px solid ${isEmergency ? '#ef4444' : (isUrgent ? '#f97316' : '#3b82f6')}; border-radius:4px; margin-bottom:0.65rem; color:${isEmergency ? '#7f1d1d' : (isUrgent ? '#7c2d12' : '#334155')}; font-weight:500;">
                    ${escapeHtml(data.warning)}
                </div>
            ` : ''}

            ${data.guidance && data.guidance.length > 0 ? `
                <p style="font-size:0.86rem; font-weight:700; margin: 0.5rem 0 0.35rem 0; color:#1e293b;">📋 Safe First-Aid Action Steps:</p>
                <ol style="padding-left:1.1rem; margin:0; font-size:0.83rem; color:#334155;">
                    ${guidanceSteps}
                </ol>
            ` : ''}

            <p style="font-size:0.75rem; color:#64748b; margin-top:0.75rem; border-top:1px solid ${borderColor}; padding-top:0.5rem;">
                ℹ️ <em>This guidance is for educational purposes and does not replace professional medical evaluation.</em>
            </p>

            <div style="margin-top:0.75rem;">
                <button class="tree-option-btn chip-btn" data-value="Start Again / Reset" style="width:100%; justify-content:center; padding:0.45rem; font-size:0.8rem; font-weight:600;">
                    🔄 Ask About Another Emergency / Symptom
                </button>
            </div>
        </div>
    `;

    appendChatMessage(botHtml, 'bot', null, true);
}

function resetChatbotState() {
    if (currentConversationId) {
        fetch('/api/chat/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conversation_id: currentConversationId })
        }).catch(err => console.error("Reset error:", err));
    }
    currentConversationId = null;

    appendChatMessage("Conversation reset. Please describe what happened or select one of the common first-aid topics below:", 'bot');
    
    const suggestionsHtml = `
        <div class="chat-suggestions" style="margin-top:0.5rem; display:flex; flex-wrap:wrap; gap:0.4rem;">
            <button class="chip-btn">Chest Pain</button>
            <button class="chip-btn">Someone is choking</button>
            <button class="chip-btn">Severe bleeding</button>
            <button class="chip-btn">Burn injury</button>
            <button class="chip-btn">Person fainted</button>
            <button class="chip-btn">Possible seizure</button>
        </div>
    `;
    appendChatMessage(suggestionsHtml, 'bot', null, true);
}

function appendChatMessage(content, sender, id = null, isHtml = false) {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${sender}`;
    if (id) msgDiv.id = id;

    if (isHtml) {
        msgDiv.innerHTML = content;
    } else {
        msgDiv.textContent = content;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function removeChatMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
