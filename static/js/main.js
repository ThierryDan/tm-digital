/* ============================================================
   ChatBot IA — JavaScript principal
   ============================================================ */

/* ── Navigation mobile ── */
(function () {
  const nav    = document.querySelector('.nav');
  const burger = document.querySelector('.nav-burger');
  if (!burger) return;

  burger.addEventListener('click', () => {
    nav.classList.toggle('menu-open');
    const open = nav.classList.contains('menu-open');
    burger.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });

  document.addEventListener('click', (e) => {
    if (!nav.contains(e.target)) {
      nav.classList.remove('menu-open');
      document.body.style.overflow = '';
    }
  });
})();

/* ── Fade-up animations ── */
(function () {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.fade-up').forEach((el) => observer.observe(el));
})();

/* ── FAQ accordéon ── */
(function () {
  document.querySelectorAll('.faq-question').forEach((btn) => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach((el) => el.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
})();

/* ── Counter animation (stats) ── */
(function () {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el     = entry.target;
        const target = parseInt(el.dataset.count, 10);
        const suffix = el.dataset.suffix || '';
        const prefix = el.dataset.prefix || '';
        let start = 0;
        const duration = 1200;
        const step = target / (duration / 16);

        const tick = () => {
          start = Math.min(start + step, target);
          el.textContent = prefix + Math.round(start) + suffix;
          if (start < target) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        observer.unobserve(el);
      });
    },
    { threshold: 0.5 }
  );

  counters.forEach((el) => observer.observe(el));
})();

/* ── Contact form ── */
(function () {
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Envoi en cours…';

    const payload = {
      nom:      form.nom.value.trim(),
      email:    form.email.value.trim(),
      entreprise: form.entreprise.value.trim(),
      secteur:  form.secteur.value,
      budget:   form.budget.value,
      message:  form.message.value.trim(),
    };

    try {
      const res = await fetch('/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error();
      form.style.display = 'none';
      document.getElementById('formSuccess').style.display = 'block';
    } catch {
      btn.disabled = false;
      btn.textContent = 'Envoyer le message';
      alert('Une erreur est survenue. Veuillez réessayer.');
    }
  });
})();

/* ── Demo chatbot ── */
(function () {
  const messagesEl = document.getElementById('cwMessages');
  const inputEl    = document.getElementById('cwInput');
  const sendBtn    = document.getElementById('cwSend');
  const tabs       = document.querySelectorAll('.sector-tab');
  const titleEl    = document.getElementById('cwTitle');

  if (!messagesEl) return;

  let history = [];
  let currentNiche = 'restaurant';

  const niches = {
    restaurant: '🍽 Assistant Restaurant',
    immobilier: '🏠 Assistant Immobilier',
  };

  function getTime() {
    return new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  }

  function addMsg(role, text) {
    const div = document.createElement('div');
    div.className = `cw-msg ${role}`;
    div.innerHTML = `
      <div class="cw-bubble">${text.replace(/\n/g, '<br>')}</div>
      <div class="cw-time">${getTime()}</div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'cw-msg bot typing-indicator';
    div.id = 'cwTyping';
    div.innerHTML = `<div class="cw-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function sendMessage() {
    const msg = inputEl.value.trim();
    if (!msg || sendBtn.disabled) return;

    inputEl.value = '';
    inputEl.style.height = 'auto';
    sendBtn.disabled = true;

    addMsg('user', msg);
    showTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, niche: currentNiche, history }),
      });
      const data = await res.json();
      document.getElementById('cwTyping')?.remove();
      history = data.history;
      addMsg('bot', data.reply);
    } catch {
      document.getElementById('cwTyping')?.remove();
      addMsg('bot', "⚠️ Une erreur s'est produite. Vérifiez que le serveur est lancé et réessayez.");
    }

    sendBtn.disabled = false;
    inputEl.focus();
  }

  if (sendBtn) sendBtn.addEventListener('click', sendMessage);

  if (inputEl) {
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    inputEl.addEventListener('input', () => {
      inputEl.style.height = 'auto';
      inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      currentNiche = tab.dataset.niche;
      history = [];
      if (titleEl) titleEl.textContent = niches[currentNiche];

      const botMessages = {
        restaurant: "Salut ! Bienvenue chez Le Moderne. C'est Marc, le gérant. Qu'est-ce que je peux faire pour toi ? 😊",
        immobilier: "Coucou ! C'est Isabelle d'Agence Prima Immo. Tu cherches un bien ? Je suis là pour trouver la maison ou l'appart de tes rêves ! 🏠"
      };

      messagesEl.innerHTML = `
        <div class="cw-msg bot">
          <div class="cw-bubble">${botMessages[currentNiche]}</div>
          <div class="cw-time">${getTime()}</div>
        </div>`;
    });
  });

  // Gestion des réservations restaurant
  if (messagesEl && currentNiche === 'restaurant') {
    const originalSendClick = sendBtn.onclick;

    sendBtn.addEventListener('click', async () => {
      const message = inputEl.value.trim();
      if (!message) return;

      inputEl.value = '';

      // Ajouter le message de l'utilisateur
      const userDiv = document.createElement('div');
      userDiv.className = 'cw-msg user';
      userDiv.innerHTML = `<div class="cw-bubble">${message}</div><div class="cw-time">${getTime()}</div>`;
      messagesEl.appendChild(userDiv);
      messagesEl.scrollTop = messagesEl.scrollHeight;

      // Détecter demande de réservation
      if (/réserv|book|reservation|table|place/i.test(message)) {
        showReservationForm();
        return;
      }

      // Sinon chatbot normal
      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, niche: currentNiche, history })
        });

        if (!res.ok) throw new Error();
        const result = await res.json();
        history = result.history;

        const botDiv = document.createElement('div');
        botDiv.className = 'cw-msg bot';
        botDiv.innerHTML = `<div class="cw-bubble">${result.reply}</div><div class="cw-time">${getTime()}</div>`;
        messagesEl.appendChild(botDiv);
        messagesEl.scrollTop = messagesEl.scrollHeight;
      } catch (e) {
        console.error(e);
      }
    });

    window.showReservationForm = function() {
      const formHTML = `
        <div style="background:rgba(26,86,219,0.1);padding:12px;border-radius:8px;margin:8px 0">
          <h4 style="margin:0 0 8px;font-size:14px">Réservation 🍽️</h4>
          <input type="text" id="resNom" placeholder="Nom" style="width:100%;padding:6px;margin-bottom:6px;border:1px solid var(--border);border-radius:4px;font-size:13px;box-sizing:border-box">
          <input type="email" id="resEmail" placeholder="Email" style="width:100%;padding:6px;margin-bottom:6px;border:1px solid var(--border);border-radius:4px;font-size:13px;box-sizing:border-box">
          <input type="date" id="resDate" style="width:100%;padding:6px;margin-bottom:6px;border:1px solid var(--border);border-radius:4px;font-size:13px;box-sizing:border-box">
          <input type="time" id="resHeure" style="width:100%;padding:6px;margin-bottom:6px;border:1px solid var(--border);border-radius:4px;font-size:13px;box-sizing:border-box">
          <select id="resPersonnes" style="width:100%;padding:6px;margin-bottom:6px;border:1px solid var(--border);border-radius:4px;font-size:13px;box-sizing:border-box">
            <option value="">Personnes</option>
            <option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option>
            <option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8">8</option><option value="9">9+</option>
          </select>
          <button id="reserveBtn" style="width:100%;padding:8px;background:var(--primary);color:white;border:0;border-radius:4px;cursor:pointer;font-weight:600;font-size:13px">Confirmer</button>
        </div>
      `;

      const div = document.createElement('div');
      div.innerHTML = formHTML;
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;

      document.getElementById('reserveBtn').onclick = async () => {
        const nom = document.getElementById('resNom').value.trim();
        const email = document.getElementById('resEmail').value.trim();
        const date = document.getElementById('resDate').value;
        const heure = document.getElementById('resHeure').value;
        const personnes = document.getElementById('resPersonnes').value;

        if (!nom || !email || !date || !heure || !personnes) {
          alert('Remplissez tous les champs');
          return;
        }

        try {
          const res = await fetch('/reservation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nom, email, date, heure, personnes })
          });

          if (!res.ok) throw new Error();

          div.remove();
          const confirmDiv = document.createElement('div');
          confirmDiv.className = 'cw-msg bot';
          confirmDiv.innerHTML = `<div class="cw-bubble">✅ Réservation confirmée! Regardez vos emails.</div><div class="cw-time">${getTime()}</div>`;
          messagesEl.appendChild(confirmDiv);
          messagesEl.scrollTop = messagesEl.scrollHeight;
        } catch (e) {
          alert('Erreur. Réessaie!');
        }
      };
    };
  }
})();
