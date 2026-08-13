#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страниц услуг friendlyai.ru из markdown.

Материалы отвечают на «как это устроено», страницы услуг — на «сделайте мне».
Разбор рынка (14.08.2026): у всех конкурентов одинаковая номенклатура услуг,
поэтому наши страницы бьют в конкретику — ИИ-агенты с ценой, отрасль (стройка),
связка с 1С и автоматизация без разработчиков.

Источник — `content/services/<slug>.md`, результат — `services/<slug>.html`.

Запускается из gen_articles.py; отдельно — для отладки:
    python3 tools/gen_services.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md import frontmatter, md_to_html, md_to_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "services"
OUT = ROOT / "services"
DOMAIN = "https://friendlyai.ru"
SITE = "FriendlyAI"
TG = "https://t.me/chilbilove"

YM = (ROOT / "tools/partials/metrika.html").read_text(encoding="utf-8").strip()

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


def load() -> list[dict]:
    items = []
    if not SRC.exists():
        return items
    for f in sorted(SRC.glob("*.md")):
        meta, body = frontmatter(f.read_text(encoding="utf-8"))
        meta.setdefault("slug", f.stem)
        text = md_to_text(body)
        meta.setdefault("title", meta["slug"])
        meta.setdefault("h1", meta["title"])
        meta.setdefault("description", text[:157].rsplit(" ", 1)[0] + "…")
        meta.setdefault("lead", meta["description"])
        meta["_body"] = body
        meta["_words"] = len(text.split())
        items.append(meta)
    return items


def faq_schema(body_html: str) -> dict | None:
    pairs = re.findall(r"<p><strong>([^<]{10,180}\?)</strong>\s*(.{40,600}?)</p>", body_html, re.S)
    if len(pairs) < 2:
        return None
    clean = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": clean(q),
                        "acceptedAnswer": {"@type": "Answer", "text": clean(a)}}
                       for q, a in pairs[:8]],
    }


def page(s: dict, others: list[dict]) -> str:
    e = html.escape
    url = f"{DOMAIN}/services/{s['slug']}.html"
    body = md_to_html(s["_body"])
    kws = s.get("keywords") or []
    kw_meta = f'\n  <meta name="keywords" content="{e(", ".join(kws))}" />' if kws else ""

    service_ld = {
        "@context": "https://schema.org", "@type": "Service",
        "name": s["h1"], "description": s["description"],
        "serviceType": s.get("service_type", s["h1"]),
        "provider": {"@type": "Organization", "name": SITE, "url": f"{DOMAIN}/"},
        "areaServed": {"@type": "Country", "name": "Россия"},
        "url": url,
    }
    crumbs = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Услуги", "item": f"{DOMAIN}/services/"},
            {"@type": "ListItem", "position": 3, "name": s["h1"], "item": url},
        ],
    }
    faq = faq_schema(body)
    faq_ld = (f'\n  <script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>'
              if faq else "")

    siblings = "".join(
        f'<li><a href="/services/{o["slug"]}.html">{e(o["h1"])}</a></li>'
        for o in others if o["slug"] != s["slug"])

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(s['title'])} — {SITE}</title>
  <meta name="description" content="{e(s['description'])}" />{kw_meta}
  <meta name="robots" content="index, follow" />
  <meta name="theme-color" content="#070a13" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="{SITE}" />
  <meta property="og:title" content="{e(s['title'])}" />
  <meta property="og:description" content="{e(s['description'])}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{DOMAIN}/assets/og-cover.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="/style.css" />
  <link rel="stylesheet" href="/article.css" />
  <script type="application/ld+json">{json.dumps(service_ld, ensure_ascii=False)}</script>
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
        <a href="/">Главная</a> · <a href="/services/">Услуги</a> · <span>{e(s['h1'])}</span>
      </nav>
      <div class="article-meta"><span>Услуга</span></div>
      <h1>{e(s['h1'])}</h1>
      <p class="article-lead">{e(s['lead'])}</p>
      <article class="article-content">
    {body}
      </article>
      <section class="article-cta">
        <h2>Разберём вашу задачу</h2>
        <p>AI-аудит: смотрим процессы, считаем, где автоматизация окупится первой, и предлагаем сценарий с понятными сроками.</p>
        <div class="article-actions">
          <a class="btn btn-primary" href="/audit.html">Запросить AI-аудит</a>
          <a class="btn btn-secondary" href="{TG}" target="_blank" rel="noopener noreferrer">Написать в Telegram</a>
        </div>
      </section>
      <aside class="article-related">
        <h2>Другие услуги</h2>
        <ul>{siblings}</ul>
      </aside>
    </div>
  </main>
  {FOOTER}
</body>
</html>
"""


def index_page(items: list[dict]) -> str:
    """services/index.html — витрина направлений."""
    cards = "".join(f"""
        <article class="news-card">
          <div class="news-meta"><span>Услуга</span></div>
          <h2><a href="/services/{i['slug']}.html">{html.escape(i['h1'])}</a></h2>
          <p>{html.escape(i['description'])}</p>
          <a class="text-link" href="/services/{i['slug']}.html">Подробнее →</a>
        </article>""" for i in items)
    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "itemListElement": [{"@type": "ListItem", "position": n + 1,
                             "url": f"{DOMAIN}/services/{i['slug']}.html", "name": i["h1"]}
                            for n, i in enumerate(items)],
    }
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Услуги: ИИ-агенты, автоматизация, интеграции — {SITE}</title>
  <meta name="description" content="Разработка ИИ-агентов под ключ, ИИ для строительных компаний, связка с 1С и автоматизация без разработчиков. Сроки, этапы и ориентиры по цене." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{DOMAIN}/services/" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Услуги — {SITE}" />
  <meta property="og:url" content="{DOMAIN}/services/" />
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
        <p>Услуги</p>
        <h1>Что мы делаем</h1>
        <p class="article-lead">Четыре направления, в которых у нас есть работающая практика, а не презентация.</p>
      </div>
      <div class="materials-list">{cards}
      </div>
    </div>
  </main>
  {FOOTER}
</body>
</html>
"""


def build() -> list[str]:
    items = load()
    if not items:
        print("страниц услуг нет")
        return []
    OUT.mkdir(parents=True, exist_ok=True)
    for s in items:
        (OUT / f"{s['slug']}.html").write_text(page(s, items), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(items), encoding="utf-8")
    print(f"собрано страниц услуг: {len(items)}")
    for s in items:
        print("  ", s["slug"], f"{s['_words']} слов")
    return [f"{DOMAIN}/services/{s['slug']}.html" for s in items] + [f"{DOMAIN}/services/"]


if __name__ == "__main__":
    build()
