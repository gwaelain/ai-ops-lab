#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка материалов friendlyai.ru из markdown-источников.

Источник правды — `content/articles/<slug>.md` (фронтматтер + markdown).
Раньше тексты статей жили внутри `js/article.js` и подставлялись браузером —
поисковый робот видел пустую страницу. Теперь каждая статья пререндерится в HTML.

Что делает:
  1. читает все .md, отбирает `publish_at` <= сегодня (капельная публикация);
  2. рендерит `news/articles/<slug>.html` — полный статический HTML;
  3. пишет `js/news.js` (список для главной) и `data/articles.json`;
  4. пересобирает `article.html` — статическую страницу «Все материалы»;
  5. обновляет `sitemap.xml` с lastmod;
  6. складывает новые URL в `tools/indexnow-new.txt` для пинга IndexNow.

Запуск:  python3 tools/gen_articles.py [--all]
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md import frontmatter, md_to_html, md_to_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "articles"
OUT = ROOT / "news" / "articles"
DOMAIN = "https://friendlyai.ru"
SITE = "FriendlyAI"
TG = "https://t.me/chilbilove"
MAIL = "Kpi1t@ya.ru"

YM = (ROOT / "tools/partials/metrika.html").read_text(encoding="utf-8").strip()

RU_MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня",
             "июля", "августа", "сентября", "октября", "ноября", "декабря"]

HEADER = """<header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/" aria-label="FriendlyAI home">
        <span class="brand-mark"><span></span></span>
        <span class="brand-copy">
          <strong>FriendlyAI</strong>
          <small>AI-агенты · Автоматизация · Результат</small>
        </span>
      </a>
      <nav class="nav" aria-label="Main navigation">
        <a href="/#solutions">Решения</a>
        <a href="/#cases">Кейсы</a>
        <a href="/#approach">Подход</a>
        <a href="/article.html">Материалы</a>
        <a href="/audit.html">AI-аудит</a>
      </nav>
      <a class="header-cta" href="%s" target="_blank" rel="noopener noreferrer">AI-аудит</a>
    </div>
  </header>""" % TG

FOOTER = """<footer class="footer">
    <div class="container footer-inner">
      <a class="brand" href="/">
        <span class="brand-mark"><span></span></span>
        <span class="brand-copy"><strong>FriendlyAI</strong><small>AI-агенты · Автоматизация · Результат</small></span>
      </a>
      <p>© 2026 FriendlyAI. AI-агенты · RAG · Автоматизация · CRM.</p>
    </div>
  </footer>"""


def ru_date(iso: str) -> str:
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return f"{d.day:02d} {RU_MONTHS[d.month - 1]} {d.year}"


def read_time(words: int) -> str:
    return f"{max(2, round(words / 180))} мин"


def load() -> list[dict]:
    arts = []
    for f in sorted(SRC.glob("*.md")):
        meta, body = frontmatter(f.read_text(encoding="utf-8"))
        meta.setdefault("slug", f.stem)
        meta.setdefault("publish_at", date.today().isoformat())
        meta.setdefault("category", "AI")
        meta.setdefault("title", meta["slug"])
        text = md_to_text(body)
        meta.setdefault("description", text[:157].rsplit(" ", 1)[0] + "…")
        meta["_body"] = body
        meta["_words"] = len(text.split())
        arts.append(meta)
    arts.sort(key=lambda a: (a["publish_at"], a["slug"]), reverse=True)
    return arts


def faq_schema(body_html: str) -> dict | None:
    """Собирает FAQPage из блоков «**Вопрос?** ответ» в конце материала.

    Разметка даёт в поиске раскрывающиеся вопросы под сниппетом — растит кликабельность.
    """
    pairs = re.findall(r"<p><strong>([^<]{10,180}\?)</strong>\s*(.{40,600}?)</p>", body_html, re.S)
    if len(pairs) < 2:
        return None
    clean = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": clean(q),
             "acceptedAnswer": {"@type": "Answer", "text": clean(a)}}
            for q, a in pairs[:8]
        ],
    }


def strip_unpublished_links(body_html: str, live_slugs: set[str]) -> str:
    """Снимает ссылки на материалы, которые ещё не вышли.

    Материалы ссылаются друг на друга, а публикуются по одному в день — до выхода
    соседа ссылка вела бы в 404. Разметку снимаем, текст оставляем; когда сосед
    выйдет, следующая сборка вернёт ссылку.
    """
    def repl(m: re.Match) -> str:
        href, text = m.group(1), m.group(2)
        mm = re.match(r"^/news/articles/([a-z0-9\-]+)\.html$", href)
        if mm and mm.group(1) not in live_slugs:
            return text
        return m.group(0)

    return re.sub(r'<a href="([^"]+)">(.*?)</a>', repl, body_html, flags=re.S)


def related(art: dict, arts: list[dict], k: int = 3) -> list[dict]:
    same = [a for a in arts if a["slug"] != art["slug"] and a["category"] == art["category"]]
    rest = [a for a in arts if a["slug"] != art["slug"] and a not in same]
    return (same + rest)[:k]


def page(a: dict, arts: list[dict]) -> str:
    e = html.escape
    url = f"{DOMAIN}/news/articles/{a['slug']}.html"
    iso = a["publish_at"]
    body = strip_unpublished_links(md_to_html(a["_body"]), {x["slug"] for x in arts})
    kws = a.get("keywords") or []
    kw_meta = f'\n  <meta name="keywords" content="{e(", ".join(kws))}" />' if kws else ""

    jsonld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["description"],
        "image": f"{DOMAIN}/assets/og-cover.png",
        "datePublished": iso, "dateModified": a.get("updated_at", iso),
        "author": {"@type": "Organization", "name": SITE, "url": f"{DOMAIN}/"},
        "publisher": {"@type": "Organization", "name": SITE,
                      "logo": {"@type": "ImageObject", "url": f"{DOMAIN}/assets/icon-512.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "inLanguage": "ru-RU",
    }
    crumbs = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Материалы", "item": f"{DOMAIN}/article.html"},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": url},
        ],
    }
    rel = "".join(
        f'<li><a href="/news/articles/{r["slug"]}.html">{e(r["title"])}</a></li>'
        for r in related(a, arts)
    )
    faq = faq_schema(body)
    faq_ld = (f'\n  <script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>'
              if faq else "")

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(a['title'])} — {SITE}</title>
  <meta name="description" content="{e(a['description'])}" />{kw_meta}
  <meta name="robots" content="index, follow" />
  <meta name="theme-color" content="#070a13" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="{SITE}" />
  <meta property="og:title" content="{e(a['title'])}" />
  <meta property="og:description" content="{e(a['description'])}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{DOMAIN}/assets/og-cover.png" />
  <meta property="article:published_time" content="{iso}" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="stylesheet" href="/style.css" />
  <link rel="stylesheet" href="/article.css" />
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(crumbs, ensure_ascii=False)}</script>{faq_ld}
{YM}
</head>
<body>
  <div class="page-bg" aria-hidden="true"></div>
  <div class="grain" aria-hidden="true"></div>
  {HEADER}
  <main class="article-page">
    <div class="container article-shell">
      <nav class="breadcrumbs" aria-label="Хлебные крошки">
        <a href="/">Главная</a> · <a href="/article.html">Материалы</a> · <span>{e(a['category'])}</span>
      </nav>
      <div class="article-meta">
        <span>{e(a['category'])}</span>
        <time datetime="{iso}">{ru_date(iso)}</time>
        <span>{read_time(a['_words'])}</span>
      </div>
      <h1>{e(a['title'])}</h1>
      <p class="article-lead">{e(a['description'])}</p>
      <article class="article-content">
    {body}
      </article>
      <section class="article-cta">
        <h2>Хотите такой же процесс у себя?</h2>
        <p>Начните с AI-аудита: разберём процессы, покажем, где автоматизация окупится первой, и предложим сценарий внедрения.</p>
        <div class="article-actions">
          <a class="btn btn-primary" href="/audit.html">Запросить AI-аудит</a>
          <a class="btn btn-secondary" href="{TG}" target="_blank" rel="noopener noreferrer">Написать в Telegram</a>
        </div>
      </section>
      <aside class="article-related">
        <h2>Читайте дальше</h2>
        <ul>{rel}</ul>
      </aside>
    </div>
  </main>
  {FOOTER}
</body>
</html>
"""


def write_lists(arts: list[dict]) -> None:
    data = [{
        "slug": a["slug"], "title": a["title"], "description": a["description"],
        "category": a["category"], "date": a["publish_at"],
        "readTime": read_time(a["_words"]),
        "url": f"news/articles/{a['slug']}.html",
    } for a in arts]
    (ROOT / "data" / "articles.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    js = "// Файл генерируется: python3 tools/gen_articles.py. Руками не править.\n"
    js += "const articles = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    (ROOT / "js" / "news.js").write_text(js, encoding="utf-8")


def write_index_page(arts: list[dict]) -> None:
    """article.html — статическая страница «Все материалы» (была JS-заглушка)."""
    cards = "".join(f"""
        <article class="news-card">
          <div class="news-meta"><span>{html.escape(a['category'])}</span><time datetime="{a['publish_at']}">{ru_date(a['publish_at'])}</time><span>{read_time(a['_words'])}</span></div>
          <h2><a href="/news/articles/{a['slug']}.html">{html.escape(a['title'])}</a></h2>
          <p>{html.escape(a['description'])}</p>
          <a class="text-link" href="/news/articles/{a['slug']}.html">Читать материал →</a>
        </article>""" for a in arts)

    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "url": f"{DOMAIN}/news/articles/{a['slug']}.html", "name": a["title"]}
            for i, a in enumerate(arts)
        ],
    }

    page_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Материалы про AI-агентов, RAG и автоматизацию — {SITE}</title>
  <meta name="description" content="Разборы про AI-агентов, RAG-системы, n8n-автоматизацию и внедрение ИИ в бизнес: практика, цифры и честные ограничения." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{DOMAIN}/article.html" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Материалы — {SITE}" />
  <meta property="og:description" content="Практика внедрения ИИ: агенты, RAG, автоматизация процессов." />
  <meta property="og:url" content="{DOMAIN}/article.html" />
  <meta property="og:image" content="{DOMAIN}/assets/og-cover.png" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="/style.css" />
  <link rel="stylesheet" href="/article.css" />
  <script type="application/ld+json">{json.dumps(itemlist, ensure_ascii=False)}</script>
{YM}
</head>
<body>
  <div class="page-bg" aria-hidden="true"></div>
  <div class="grain" aria-hidden="true"></div>
  {HEADER}
  <main class="article-page">
    <div class="container">
      <div class="section-head">
        <p>Материалы</p>
        <h1>Разборы про AI-агентов, RAG и автоматизацию</h1>
        <p class="article-lead">Пишем то, что проверили руками: где ИИ даёт результат, где ломается и сколько это стоит на самом деле.</p>
      </div>
      <div class="materials-list">{cards}
      </div>
    </div>
  </main>
  {FOOTER}
</body>
</html>
"""
    (ROOT / "article.html").write_text(page_html, encoding="utf-8")


def update_index_html(arts: list[dict], k: int = 4) -> None:
    """Свежие материалы на главной статикой — ускоряет обход новых страниц."""
    f = ROOT / "index.html"
    txt = f.read_text(encoding="utf-8")
    if "<!-- latest:auto -->" not in txt:
        return
    items = "".join(f'''
          <article class="news-card">
            <div class="news-meta"><span>{html.escape(a["category"])}</span><time datetime="{a["publish_at"]}">{ru_date(a["publish_at"])}</time></div>
            <h3><a href="/news/articles/{a["slug"]}.html">{html.escape(a["title"])}</a></h3>
            <p>{html.escape(a["description"])}</p>
          </article>''' for a in arts[:k])
    block = ('      <!-- latest:auto -->\n'
             f'      <div class="container materials-list">{items}\n      </div>\n'
             '      <!-- /latest:auto -->')
    txt = re.sub(r"      <!-- latest:auto -->.*?<!-- /latest:auto -->", block, txt, flags=re.S)
    f.write_text(txt, encoding="utf-8")


def update_sitemap(arts: list[dict]) -> None:
    today = date.today().isoformat()
    static = [("/", "1.0"), ("/article.html", "0.9"), ("/cases.html", "0.8"), ("/audit.html", "0.9")]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, pri in static:
        lines.append(f"  <url><loc>{DOMAIN}{path}</loc><lastmod>{today}</lastmod><priority>{pri}</priority></url>")
    for a in arts:
        lines.append(
            f"  <url><loc>{DOMAIN}/news/articles/{a['slug']}.html</loc>"
            f"<lastmod>{a.get('updated_at', a['publish_at'])}</lastmod><priority>0.7</priority></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    show_all = "--all" in sys.argv
    today = date.today().isoformat()
    arts = load()
    live = arts if show_all else [a for a in arts if a["publish_at"] <= today]

    OUT.mkdir(parents=True, exist_ok=True)
    # список опубликованного держим файлом: наличие html на диске больше не признак
    # публикации — собранные страницы едут в репозиторий вместе с исходниками
    seen_file = ROOT / "tools" / "published.json"
    seen = set(json.loads(seen_file.read_text(encoding="utf-8"))) if seen_file.exists() else set()

    fresh = []
    for a in live:
        name = f"{a['slug']}.html"
        if a["slug"] not in seen:
            fresh.append(f"{DOMAIN}/news/articles/{name}")
        (OUT / name).write_text(page(a, live), encoding="utf-8")
    seen_file.write_text(json.dumps(sorted(seen | {a["slug"] for a in live}),
                                    ensure_ascii=False, indent=1), encoding="utf-8")

    write_lists(live)
    write_index_page(live)
    update_index_html(live)
    update_sitemap(live)
    (ROOT / "tools" / "indexnow-new.txt").write_text("\n".join(fresh), encoding="utf-8")

    print(f"опубликовано материалов: {len(live)} (новых: {len(fresh)}), "
          f"ждут даты: {len(arts) - len(live)}")
    for a in live[:5]:
        print("  ", a["slug"], a["publish_at"], f"{a['_words']} слов")


if __name__ == "__main__":
    main()
