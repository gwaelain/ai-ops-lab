# FriendlyAI

AI-агенты · Автоматизация · Результат

FriendlyAI — сайт Студия AI-автоматизации: AI-агенты, RAG-системы, n8n-автоматизация, AI-секретари, голосовые роботы и CRM/ERP-интеграции.

## Website

https://friendlyai.ru

## Как устроен контент

Источник правды — markdown, HTML генерируется:

```
python tools/gen_articles.py      # материалы + страницы услуг + sitemap + списки
python tools/indexnow.py          # пинг Яндекса о новых URL
```

- `content/articles/<slug>.md` → `news/articles/<slug>.html` (материалы блога).
  Поле `publish_at` — капельная публикация: до этой даты страницы не существует.
- `content/services/<slug>.md` → `services/<slug>.html` (страницы услуг, приоритет 0.9).
- Разметка: JSON-LD Article / Service + BreadcrumbList + FAQPage (собирается из блоков
  «**Вопрос?** ответ»), canonical, OG, хлебные крошки, перелинковка.
- Ежедневную публикацию делает задача Планировщика на машине владельца
  (`infra\scripts\drip-friendlyai.ps1`) — GitHub-токен без scope `workflow`,
  поэтому Actions временно не используются.

Темы и ключи — `_content\_klyuchi\friendlyai\klyuchi.md`, разбор рынка —
`_content\_klyuchi\RYNOK-2026-08-14.md`.

## Structure

```text
/
├── index.html
├── article.html
├── style.css
├── robots.txt
├── sitemap.xml
├── CNAME
├── 404.html
├── site.webmanifest
├── humans.txt
├── .nojekyll
├── assets/
├── data/
├── js/
└── news/articles/
```

## Contacts

Telegram: https://t.me/chilbilove
Почта: Kpi1t@ya.ru
