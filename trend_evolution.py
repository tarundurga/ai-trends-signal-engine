import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

SIGNAL_FILES = [
    "rss_signals.json",
    "ats_jobs_largecap_signals.json",
    "ats_jobs_midcap_signals.json"
]

THEME_FILE = "THEME_REGISTRY.json"
OUTPUT_FILE = "trend_history.json"

def load_json(path):
    if not Path(path).exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_themes(text, theme_registry):
    hits = []
    t = (text or "").lower()
    for theme, cfg in theme_registry.items():
        if any(k in t for k in cfg["keywords"]):
            hits.append(theme)
    return hits

def main():
    theme_registry = load_json(THEME_FILE)
    if not theme_registry:
        raise ValueError("Theme registry missing or empty")

    all_signals = []
    for f in SIGNAL_FILES:
        all_signals.extend(load_json(f))

    week_key = datetime.utcnow().strftime("%Y-W%U")

    weekly_counts = defaultdict(lambda: {
        "total": 0,
        "largecap": 0,
        "midcap": 0
    })

    for s in all_signals:
        text = f"{s.get('title','')} {s.get('snippet','')}"
        themes = detect_themes(text, theme_registry)
        for theme in themes:
            weekly_counts[theme]["total"] += 1
            if s.get("segment") == "largecap":
                weekly_counts[theme]["largecap"] += 1
            elif s.get("segment") == "midcap":
                weekly_counts[theme]["midcap"] += 1

    history = load_json(OUTPUT_FILE)
    history.append({
        "week": week_key,
        "themes": weekly_counts
    })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"Trend snapshot saved for {week_key}")

if __name__ == "__main__":
    main()
