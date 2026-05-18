const articles = [
  {
    slug: 'corporate-rag-agent',
    title: 'Корпоративный RAG-агент: как превратить документы в рабочую базу знаний',
    description: 'Разбираем, как RAG помогает поддержке, продажам и операционным командам отвечать быстрее и точнее.',
    category: 'RAG',
    date: '2026-01-12',
    readTime: '6 мин',
    url: 'news/articles/corporate-rag-agent.html'
  },
  {
    slug: 'ai-sales-crm',
    title: 'AI в продажах: как агент квалифицирует лиды и обновляет CRM',
    description: 'Практический сценарий: входящая заявка, уточняющие вопросы, скоринг и передача менеджеру.',
    category: 'Sales',
    date: '2026-01-10',
    readTime: '5 мин',
    url: 'news/articles/ai-sales-crm.html'
  },
  {
    slug: 'voice-ai-first-line',
    title: 'Голос AI как первая линия клиентского сервиса',
    description: 'Когда голосовой робот уместен, где нужны ограничения и как передавать результат человеку.',
    category: 'Голос AI',
    date: '2026-01-08',
    readTime: '4 мин',
    url: 'news/articles/voice-ai-first-line.html'
  },
  {
    slug: 'n8n-ai-crm-процесс',
    title: 'n8n + AI + CRM: минимальный контур автоматизации',
    description: 'Схема, которая связывает формы, Telegram, почту, AI-логику и CRM без лишней сложности.',
    category: 'Автоматизация',
    date: '2026-01-05',
    readTime: '5 мин',
    url: 'news/articles/n8n-ai-crm-процесс.html'
  }
];

const grid = document.querySelector('[data-news-grid]');
const filters = document.querySelector('[data-news-filters]');

function formatDate(dateString) {
  return new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(dateString));
}

function cardTemplate(article) {
  return `
    <article class="news-card">
      <div class="news-image" aria-hidden="true"></div>
      <div class="news-body">
        <div class="news-meta"><span>${article.category}</span><time>${formatDate(article.date)}</time></div>
        <h3>${article.title}</h3>
        <p>${article.description}</p>
        <a href="${article.url}">Читать →</a>
      </div>
    </article>
  `;
}

function render(category = 'Все') {
  if (!grid) return;
  const items = category === 'Все' ? articles : articles.filter((article) => article.category === category);
  grid.innerHTML = items.map(cardTemplate).join('');
}

function renderFilters() {
  if (!filters) return;
  const categories = ['Все', ...new Set(articles.map((article) => article.category))];
  filters.innerHTML = categories.map((category, index) => `<button class="news-filter ${index === 0 ? 'active' : ''}" type="button" data-category="${category}">${category}</button>`).join('');
  filters.addEventListener('click', (event) => {
    const button = event.target.closest('[data-category]');
    if (!button) return;
    filters.querySelectorAll('.news-filter').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    render(button.dataset.category);
  });
}

renderFilters();
render();
