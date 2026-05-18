from pathlib import Path
import json, html

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "news.json"
OUTPUT_DIR = ROOT / "news" / "articles"
DOMAIN = "https://friendlyai.ru"

def render_content(blocks):
    out = []
    for b in blocks:
        if b["type"] == "h2":
            out.append(f"<h2>{html.escape(b['text'])}</h2>")
        elif b["type"] == "p":
            out.append(f"<p>{html.escape(b['text'])}</p>")
        elif b["type"] == "ul":
            out.append("<ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in b["items"]) + "</ul>")
    return "\\n".join(out)

def build():
    news = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for item in news:
        slug = item.get("slug") or item["id"]
        page = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><title>{html.escape(item['title'])} — FriendlyAI</title><meta name="description" content="{html.escape(item['description'])}"/><link rel="canonical" href="{DOMAIN}/news/articles/{slug}.html"/><link rel="stylesheet" href="../../style.css"/></head><body><div class="aurora"></div><div class="mesh"></div><header class="site-header"><div class="container header-inner"><a class="brand" href="../../index.html"><span class="brand-icon"><span></span></span><span class="brand-text"><strong>FriendlyAI</strong><small>Agents · Automation · ROI</small></span></a><a class="header-action" href="https://t.me/chilbilove" target="_blank" rel="noopener noreferrer">AI-аудит</a></div></header><main class="article-page"><div class="container"><div class="article-hero"><a class="back-link" href="../../index.html#news">← Все новости</a><div class="article-meta"><span>{item['category']}</span><time datetime="{item['date']}">{item['date']}</time><span>{item.get('readTime','5 мин')}</span></div><h1>{html.escape(item['title'])}</h1><p>{html.escape(item['description'])}</p><img src="../../{item['image']}" alt="{html.escape(item['title'])}"></div><article class="article-content">{render_content(item.get('content', []))}</article></div></main></body></html>"""
        (OUTPUT_DIR / f"{slug}.html").write_text(page, encoding="utf-8")

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', f"<url><loc>{DOMAIN}/</loc><priority>1.0</priority></url>"]
    for item in news:
        slug = item.get("slug") or item["id"]
        sitemap.append(f"<url><loc>{DOMAIN}/news/articles/{slug}.html</loc><priority>0.8</priority></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\\n".join(sitemap), encoding="utf-8")
    print(f"Generated {len(news)} articles and sitemap.xml")

if __name__ == "__main__":
    build()
