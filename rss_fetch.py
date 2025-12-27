import feedparser
import requests
from datetime import datetime
import json

# ---- CONFIG ----

RSS_FEEDS = [
    # India-first
    ("Mint - Tech", "https://www.livemint.com/rss/technology"),
    ("Business Standard - Tech", "https://www.business-standard.com/rss/technology-108.rss"),
    ("Indian Express - Tech", "https://indianexpress.com/section/technology/feed/"),
    ("ET - Tech", "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms"),

    # Global
    ("FT - Technology", "https://www.ft.com/technology?format=rss"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),

    # Consulting
    ("McKinsey", "https://www.mckinsey.com/featured-insights/rss"),
    ("BCG", "https://www.bcg.com/rss"),
]

OUTPUT_FILE = "rss_signals.json"

# ---- FETCH ----

signals = []

for source_name, feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:10]:  # limit per feed
        signals.append({
            "captured_at": datetime.utcnow().isoformat(),
            "source_channel": "rss",
            "source_type": "news",
            "geo_primary": "India" if "Mint" in source_name or "Indian" in source_name or "ET" in source_name else "Global",
            "india_relevance": "High" if "India" in source_name or "Mint" in source_name else "Medium",
            "org_name": "",
            "industry": "",
            "role_or_skill_hint": "",
            "title": entry.get("title", ""),
            "snippet": entry.get("summary", "")[:300],
            "link": entry.get("link", ""),
            "evidence_weight": 3,
            "notes": source_name
        })

# ---- SAVE ----

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(signals, f, indent=2)

print(f"Saved {len(signals)} RSS signals")
