/* Chat Widget JavaScript */
(function() {
  // Configuration
  const CONFIG = {
    telegramUrl: 'https://t.me/TMDigitalBot',
    whatsappUrl: 'https://wa.me/32465741025?text=Bonjour,%20j%27aimerais%20discuter%20avec%20le%20chatbot%20de%20TM%20Digital',
    telegramPhone: '+32 465 74 10 25',
    whatsappPhone: '+32 465 74 10 25'
  };

  // Créer le widget HTML
  function createWidget() {
    const container = document.createElement('div');
    container.className = 'chat-widget-container';
    container.innerHTML = `
      <button class="chat-widget-bubble pulse" id="chatWidgetBubble" aria-label="Chat avec nous">
        💬
      </button>

      <div class="chat-widget-menu" id="chatWidgetMenu">
        <div class="chat-widget-header">
          <h3>Parlons de votre projet</h3>
          <p>Disponible 24/7</p>
        </div>

        <div class="chat-widget-buttons">
          <a href="${CONFIG.telegramUrl}" target="_blank" rel="noopener noreferrer" class="chat-widget-button telegram">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.5 10l-4 2.5v-5l4 2.5zm-7 0l4-2.5v5l-4-2.5z"/>
            </svg>
            <div class="chat-widget-button-text">
              <strong>Telegram</strong>
              <small>Réponse immédiate</small>
            </div>
          </a>

          <a href="${CONFIG.whatsappUrl}" target="_blank" rel="noopener noreferrer" class="chat-widget-button whatsapp">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.471 16.596c-.268-.07-.945-.468-1.088-.52-.143-.052-.247-.07-.35.07-.104.14-.403.52-.494.624-.09.105-.182.117-.45.035-.268-.07-1.076-.397-2.051-1.263-.759-.678-1.271-1.516-1.418-1.784-.147-.268-.016-.412.11-.544.112-.112.247-.294.371-.441.123-.147.165-.247.247-.412.083-.165.042-.31-.02-.433-.063-.123-.35-.844-.479-1.155-.126-.289-.252-.25-.35-.255-.09-.005-.186-.005-.28-.005-.095 0-.247.035-.378.175-.13.14-.498.487-.498.487-.248-.248-.248-.248-.248-.248 0-1.068.505-2.052 1.404-2.795 1.05-.879 2.475-1.38 4.017-1.38 1.069 0 2.062.265 2.94.728 1.45.767 2.383 2.213 2.383 3.873 0 1.067-.268 2.105-.754 3.015-.283.541-.631 1.04-1.03 1.488z"/>
            </svg>
            <div class="chat-widget-button-text">
              <strong>WhatsApp</strong>
              <small>Chat instantané</small>
            </div>
          </a>
        </div>
      </div>
    `;

    document.body.appendChild(container);

    // Event listeners
    const bubble = document.getElementById('chatWidgetBubble');
    const menu = document.getElementById('chatWidgetMenu');

    bubble.addEventListener('click', () => {
      bubble.classList.toggle('active');
      menu.classList.toggle('active');
    });

    // Fermer le menu quand on clique ailleurs
    document.addEventListener('click', (e) => {
      if (!container.contains(e.target)) {
        bubble.classList.remove('active');
        menu.classList.remove('active');
      }
    });

    // Fermer le menu avec la touche Échap
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        bubble.classList.remove('active');
        menu.classList.remove('active');
      }
    });
  }

  // Attendre que le DOM soit prêt
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createWidget);
  } else {
    createWidget();
  }
})();
