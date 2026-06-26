/* Live Chat Widget */
(function() {
  const chatHTML = `
    <div class="live-chat-container">
      <div class="live-chat-header">
        <h3>💬 Assistant IA</h3>
        <button class="live-chat-close" aria-label="Fermer le chat">&times;</button>
      </div>
      <div class="live-chat-messages" id="liveChatMessages"></div>
      <div class="live-chat-input-area">
        <input type="text" id="liveChatInput" placeholder="Tapez votre question..." maxlength="500" />
        <button id="liveChatSend" aria-label="Envoyer">📤</button>
      </div>
    </div>
  `;

  const chatCSS = `
    .live-chat-container {
      position: fixed;
      bottom: 100px;
      right: 20px;
      width: 380px;
      max-height: 600px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 5px 40px rgba(0,0,0,0.16);
      display: flex;
      flex-direction: column;
      z-index: 9998;
      font-family: inherit;
    }

    .live-chat-header {
      background: linear-gradient(135deg, var(--primary) 0%, #0066cc 100%);
      color: white;
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 12px 12px 0 0;
    }

    .live-chat-header h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }

    .live-chat-close {
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .live-chat-close:hover {
      opacity: 0.8;
    }

    .live-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .live-chat-message {
      display: flex;
      gap: 8px;
      animation: slideIn 0.3s ease;
    }

    .live-chat-message.user {
      justify-content: flex-end;
    }

    .live-chat-message-bubble {
      max-width: 70%;
      padding: 12px 14px;
      border-radius: 12px;
      font-size: 14px;
      line-height: 1.4;
      word-wrap: break-word;
    }

    .live-chat-message.assistant .live-chat-message-bubble {
      background: #f0f0f0;
      color: #333;
    }

    .live-chat-message.user .live-chat-message-bubble {
      background: linear-gradient(135deg, var(--primary) 0%, #0066cc 100%);
      color: white;
    }

    .live-chat-input-area {
      display: flex;
      gap: 8px;
      padding: 12px;
      border-top: 1px solid #e0e0e0;
      background: white;
      border-radius: 0 0 12px 12px;
    }

    #liveChatInput {
      flex: 1;
      border: 1px solid #e0e0e0;
      border-radius: 20px;
      padding: 10px 16px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }

    #liveChatInput:focus {
      border-color: var(--primary);
    }

    #liveChatSend {
      background: linear-gradient(135deg, var(--primary) 0%, #0066cc 100%);
      border: none;
      color: white;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      cursor: pointer;
      font-size: 16px;
      transition: transform 0.2s;
    }

    #liveChatSend:hover:not(:disabled) {
      transform: scale(1.05);
    }

    #liveChatSend:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .live-chat-typing {
      display: flex;
      gap: 4px;
      align-items: center;
    }

    .live-chat-typing span {
      width: 8px;
      height: 8px;
      background: #999;
      border-radius: 50%;
      animation: typing 1.4s infinite;
    }

    .live-chat-typing span:nth-child(2) {
      animation-delay: 0.2s;
    }

    .live-chat-typing span:nth-child(3) {
      animation-delay: 0.4s;
    }

    @keyframes typing {
      0%, 60%, 100% { opacity: 0.5; }
      30% { opacity: 1; }
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @media (max-width: 640px) {
      .live-chat-container {
        width: calc(100vw - 40px);
        max-height: 70vh;
        bottom: 90px;
        right: 20px;
      }

      .live-chat-message-bubble {
        max-width: 85%;
      }
    }
  `;

  // Ajouter les styles
  const style = document.createElement('style');
  style.textContent = chatCSS;
  document.head.appendChild(style);

  // Créer le chat
  const container = document.createElement('div');
  container.innerHTML = chatHTML;
  document.body.appendChild(container);

  const chatContainer = container.querySelector('.live-chat-container');
  const messagesDiv = document.getElementById('liveChatMessages');
  const input = document.getElementById('liveChatInput');
  const sendBtn = document.getElementById('liveChatSend');
  const closeBtn = container.querySelector('.live-chat-close');

  let isLoading = false;

  // Fermer le chat
  closeBtn.addEventListener('click', () => {
    chatContainer.style.display = 'none';
  });

  // Envoyer un message
  async function sendMessage() {
    const message = input.value.trim();
    if (!message || isLoading) return;

    // Afficher le message utilisateur
    addMessage(message, 'user');
    input.value = '';

    isLoading = true;
    sendBtn.disabled = true;
    showTyping();

    try {
      // Envoyer au serveur
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, niche: 'tmdigital' })
      });

      if (!response.ok) throw new Error('Erreur serveur');

      const data = await response.json();
      removeTyping();
      addMessage(data.reply, 'assistant');
    } catch (error) {
      removeTyping();
      addMessage('Désolé, j\'ai une erreur technique. Réessayez!', 'assistant');
      console.error('Chat error:', error);
    }

    isLoading = false;
    sendBtn.disabled = false;
    input.focus();
  }

  function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = `live-chat-message ${role}`;
    div.innerHTML = `<div class="live-chat-message-bubble">${text}</div>`;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'live-chat-message assistant';
    div.id = 'typing-indicator';
    div.innerHTML = '<div class="live-chat-typing"><span></span><span></span><span></span></div>';
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function removeTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
  }

  // Event listeners
  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });

  // Message de bienvenue
  setTimeout(() => {
    addMessage('👋 Bonjour! Comment puis-je vous aider?', 'assistant');
  }, 500);
})();
