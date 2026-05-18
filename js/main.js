const revealItems = document.querySelectorAll('.section-reveal');

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('visible'));
}


const canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
if (canHover) {
  const glow = document.createElement('div');
  glow.className = 'mouse-glow';
  document.body.appendChild(glow);
  window.addEventListener('pointermove', (event) => {
    glow.style.left = `${event.clientX}px`;
    glow.style.top = `${event.clientY}px`;
  }, { passive: true });
}

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

// Static AI-audit form helper. Creates a compact brief and opens Telegram.
document.querySelectorAll('[data-audit-form]').forEach((form) => {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const name = (data.get('name') || '').toString().trim() || 'Не указано';
    const contact = (data.get('contact') || '').toString().trim() || 'Не указано';
    const task = (data.get('task') || '').toString().trim() || 'Не указано';
    const text = `Заявка на AI-аудит FriendlyAI\n\nИмя/компания: ${name}\nКонтакт: ${contact}\nЗадача: ${task}`;
    const note = form.querySelector('[data-form-note]');
    try {
      await navigator.clipboard.writeText(text);
      if (note) note.textContent = 'Заявка скопирована. Вставьте её в Telegram-диалог.';
    } catch (error) {
      if (note) note.textContent = 'Заявка сформирована. Скопируйте текст из полей и отправьте в Telegram.';
    }
    window.open('https://t.me/chilbilove', '_blank', 'noopener,noreferrer');
  });
});

// Light premium tilt for cards on desktop.
if (canHover) {
  document.querySelectorAll('.solution-card,.case-card,.news-card,.dash-card').forEach((card) => {
    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      card.style.transform = `translateY(-5px) rotateX(${(-y * 2).toFixed(2)}deg) rotateY(${(x * 2).toFixed(2)}deg)`;
    });
    card.addEventListener('pointerleave', () => {
      card.style.transform = '';
    });
  });
}
