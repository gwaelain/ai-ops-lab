# FriendlyAI

AI-агенты · Автоматизация · Результат

FriendlyAI — сайт Студия AI-автоматизации: AI-агенты, RAG-системы, n8n-автоматизация, AI-секретари, голосовые роботы и CRM/ERP-интеграции.

## Website

https://friendlyai.ru

## ⚠️ Правило: работаем только через git, и всегда сначала подтягиваем

Сайт публикует себя сам: на сервере 5.188.27.237 лежит клон репозитория
(`/opt/drip/ai-ops-lab`), скрипт `/opt/drip/friendlyai-publish.sh` по cron (`20 7` ежедневно
и `*/10` — подхват свежих пушей) делает `git fetch` → собирает материалы, у которых наступил
`publish_at` → раскладывает статику в `/opt/static/friendlyai` → пингует IndexNow →
**коммитит результат и пушит обратно**. Поэтому `origin/main` регулярно уходит вперёд копии.

**Перед любой правкой:** `infra\scripts\sync-saity.ps1` (подтянет оба сайта; репозиторий
с незакоммиченными правками пропустит, чтобы ничего не потерять).
Вручную: `git fetch origin && git reset --hard origin/main`.

**Как выкатывать:** правишь исходники → коммит → `git push`, через 10 минут сервер подхватит.
Ручная заливка `infra\scripts\deploy-friendlyai.ps1` — запасной путь; после неё всё равно
нужен пуш, иначе сервер затрёт правки своей версией.

**Руками не редактировать** (перезапишется при сборке): `news/articles/*.html`,
`services/*.html`, `article.html`, `js/news.js`, `data/articles.json`, `sitemap.xml`,
`tools/published.json`, блоки между `<!-- latest:auto -->`.

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
