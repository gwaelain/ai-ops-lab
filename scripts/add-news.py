from pathlib import Path
from datetime import date
import json, re

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "news.json"

def slugify(text):
    text = text.lower()
    table = {"а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"h","ц":"c","ч":"ch","ш":"sh","щ":"sch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya"}
    for ru,en in table.items(): text = text.replace(ru,en)
    return re.sub(r"[^a-z0-9]+","-",text).strip("-")

title = input("Title: ").strip()
category = input("Category: ").strip() or "AI"
description = input("Description: ").strip()
image = input("Image [assets/news-rag.svg]: ").strip() or "assets/news-rag.svg"
slug = slugify(title)

news = json.loads(DATA_FILE.read_text(encoding="utf-8"))
news.append({
    "id": slug,
    "slug": slug,
    "category": category,
    "date": str(date.today()),
    "title": title,
    "description": description,
    "image": image,
    "staticUrl": f"news/articles/{slug}.html",
    "readTime": "5 мин",
    "tags": [category],
    "content": [
        {"type": "p", "text": description},
        {"type": "h2", "text": "Почему это важно"},
        {"type": "p", "text": "Добавьте основной текст раздела."}
    ]
})
DATA_FILE.write_text(json.dumps(news, ensure_ascii=False, indent=2), encoding="utf-8")
print("Added:", slug)
print("Run: python scripts/generate-static-news.py")
