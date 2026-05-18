const articleДанные = {
  'corporate-rag-agent': {
    title: 'Корпоративный RAG-агент: как превратить документы в рабочую базу знаний',
    description: 'RAG-система помогает AI отвечать не из общего интернета, а из проверенных материалов компании: регламентов, инструкций, прайсов, FAQ и внутренних документов.',
    category: 'RAG', date: '2026-01-12', readTime: '6 мин',
    content: [
      ['Зачем бизнесу RAG', 'Обычный чат-бот быстро упирается в ограничение: он не знает актуальных внутренних правил компании. RAG-агент получает доступ к базе знаний и формирует ответ на основе конкретных фрагментов документов.'],
      ['Где это работает лучше всего', 'Поддержка клиентов, обучение сотрудников, продажи, технические консультации, работа с регламентами, подбор товаров и быстрый поиск по внутренним материалам.'],
      ['Что важно учесть', 'Нужны чистые источники данных, роли доступа, логика обновления документов, проверка ответов, fallback-сценарии и понятные метрики качества.']
    ]
  },
  'ai-sales-crm': {
    title: 'AI в продажах: как агент квалифицирует лиды и обновляет CRM',
    description: 'AI-агент может принять входящую заявку, задать уточняющие вопросы, определить потенциал клиента и передать менеджеру уже подготовленную карточку.',
    category: 'Sales', date: '2026-01-10', readTime: '5 мин',
    content: [
      ['Сценарий работы', 'Клиент оставляет заявку на сайте или пишет в Telegram. Агент уточняет задачу, бюджет, сроки и контактные данные, затем создаёт сделку в CRM.'],
      ['Что получает менеджер', 'Не сырой лид, а краткую сводку: потребность, контекст, степень готовности, следующие шаги и историю диалога.'],
      ['Как считать эффект', 'Скорость реакции, доля обработанных лидов, конверсия в встречу, нагрузка менеджеров и качество заполнения CRM.']
    ]
  },
  'voice-ai-first-line': {
    title: 'Голос AI как первая линия клиентского сервиса',
    description: 'Голосовой AI закрывает повторяемые звонки, но должен иметь понятные ограничения и корректную передачу сложных случаев человеку.',
    category: 'Голос AI', date: '2026-01-08', readTime: '4 мин',
    content: [
      ['Когда голосовой агент уместен', 'Подтверждение заявок, напоминания, первичная квалификация, сбор данных, ответы на типовые вопросы и маршрутизация обращений.'],
      ['Главное правило', 'Робот не должен имитировать компетенцию там, где нужен человек. Нужны ограничения, сценарии выхода и корректная передача результата оператору.'],
      ['Интеграция', 'После звонка система создаёт задачу, обновляет CRM, отправляет сводку и фиксирует статус обращения.']
    ]
  },
  'n8n-ai-crm-процесс': {
    title: 'n8n + AI + CRM: минимальный контур автоматизации',
    description: 'Минимальный контур соединяет форму заявки, Telegram, почту, AI-обработку, CRM и уведомления команды.',
    category: 'Автоматизация', date: '2026-01-05', readTime: '5 мин',
    content: [
      ['Базовая схема', 'Форма или сообщение запускает webhook. n8n собирает данные, AI классифицирует запрос, CRM получает сделку, команда получает уведомление.'],
      ['Почему это удобно', 'Сценарий легко дорабатывать: добавлять проверки, разные ветки, интеграции, обработку ошибок и отчёты.'],
      ['С чего начать', 'Лучше выбрать один повторяемый процесс, собрать MVP и измерить экономию времени до масштабирования.']
    ]
  }
};

const root = document.querySelector('[data-article]');

function formatDate(dateString) {
  return new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(dateString));
}

function getSlug() {
  const path = window.location.pathname.split('/').pop().replace('.html', '');
  const params = new URLSearchParams(window.location.search);
  return articleДанные[path] ? path : params.get('slug');
}

function listTemplate() {
  const cards = Object.entries(articleДанные).map(([slug, article]) => `
    <article class="news-card">
      <div class="news-image" aria-hidden="true"></div>
      <div class="news-body">
        <div class="news-meta"><span>${article.category}</span><time>${formatDate(article.date)}</time></div>
        <h3>${article.title}</h3>
        <p>${article.description}</p>
        <a href="news/articles/${slug}.html">Читать →</a>
      </div>
    </article>
  `).join('');

  return `
    <div class="article-shell section-reveal visible">
      <a class="back-link" href="index.html">← На главную</a>
      <h1>Материалы FriendlyAI</h1>
      <p class="article-lead">Короткие практические разборы про AI-агентов, RAG, n8n и автоматизацию бизнес-процессов.</p>
      <div class="article-list">${cards}</div>
    </div>
  `;
}

function articleTemplate(article) {
  const content = article.content.map(([heading, text]) => `<h2>${heading}</h2><p>${text}</p>`).join('');
  return `
    <article class="article-shell section-reveal visible">
      <a class="back-link" href="../../index.html#news">← К материалам</a>
      <div class="article-meta"><span>${article.category}</span><time>${formatDate(article.date)}</time><span>${article.readTime}</span></div>
      <h1>${article.title}</h1>
      <p class="article-lead">${article.description}</p>
      <div class="article-visual" aria-hidden="true"></div>
      <div class="article-content">${content}</div>
      <div class="article-cta">
        <h2>Хотите внедрить похожий сценарий?</h2>
        <p>Опишите процесс, который хотите автоматизировать. Мы подскажем, с какого MVP лучше начать.</p>
        <div class="hero-actions"><a class="btn btn-primary" href="https://t.me/chilbilove" target="_blank" rel="noopener noreferrer">Обсудить проект</a></div>
      </div>
    </article>
  `;
}

if (root) {
  const slug = getSlug();
  root.innerHTML = slug && articleДанные[slug] ? articleTemplate(articleДанные[slug]) : listTemplate();
}
