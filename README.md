# FriendlyAI / AI Ops Lab — News Engine

## Заменить в репозитории
- `index.html`
- `style.css`
- `article.html`
- `robots.txt`
- `sitemap.xml`
- `README.md`

## Добавить в репозиторий
- `data/news.json`
- `js/news.js`
- `js/article.js`
- `assets/news-rag.svg`
- `assets/news-sales.svg`
- `assets/news-voice.svg`
- `assets/news-n8n.svg`
- `news/articles/*.html`
- `news/images/`
- `scripts/generate-static-news.py`
- `scripts/add-news.py`
- `article-template.html`

## Как работает
- Главная страница сама выводит новости из `data/news.json`
- Фильтры по категориям создаются автоматически
- Статьи можно читать по ссылкам `news/articles/*.html`
- Новые новости добавляются через `data/news.json`
- После добавления можно запустить:
  `python scripts/generate-static-news.py`

## Домен
Файлы настроены под:
https://friendlyai.ru
