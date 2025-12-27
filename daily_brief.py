import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

TODAY = datetime.utcnow().date()
YESTERDAY = TODAY - timedelta(days=1)

FILES = [
    "rss_signals.json",
    "ats_jobs_largecap_signals.json",
    "ats_jobs_midcap_signals.json"
]

OUTPUT_FILE = "daily_brief.md"

THEMES = {
    "AI Fluency & Literacy": ["training", "enablement", "fluency", "academy"],
    "Role Redesign": ["role", "responsibility", "job architecture"],
    "Governance & Risk": ["governance", "guardrails", "risk", "responsible"],
    "Agentic Workflows": ["agent", "orchestration", "automation"],
    "Creative / Design AI": ["design", "ux", "content", "creative"]
}

def load_signals():
    signals = []
    for f in FILES:
        if Path(f).exists():
            with open(f, "r", encoding="utf-8") as fh:
                try:
                    data = json.load(fh)
                    signals.extend(data)
                except Exception:
                    pass
    return signals

def is_recent(sig):
    try:
        d = datetime.fromisoformat(sig.get("captured_at", "")).date()
        return d >= YESTERDAY
    except Exception:
        return False

def detect_themes(sig):
    text = (sig.get("title","") + " " + sig.get("snippet","")).lower()
    hits = []
    for theme, kws in THEMES.items():
        if any(k in text for k in kws):
            hits.append(theme)
    return hits or ["Unclassified"]

def main():
    signals = [s for s in load_signals() if is_recent(s)]

    by_theme = defaultdict(list)
    by_segment = defaultdict(list)
    skills = Counter()

    for s in signals:
        themes = detect_themes(s)
        for t in themes:
            by_theme[t].append(s)

        seg = s.get("segment","unknown")
        by_segment[seg].append(s)

        for sk in s.get("skill_hits", []):
            skills[sk] += 1

    strengthening = "\n".join(
        f"- **{t}** ({len(v)} signals)"
        for t, v in sorted(by_theme.items(), key=lambda x: len(x[1]), reverse=True)
        if len(v) >= 2
    ) or "- No strong convergence yet"

    seg_diff = []
    if by_segment.get("largecap") and by_segment.get("midcap"):
        seg_diff.append(
            f"- **Largecaps** showing more institutional signals ({len(by_segment['largecap'])})"
        )
        seg_diff.append(
            f"- **Midcaps** showing more role/skill experimentation ({len(by_segment['midcap'])})"
        )
    else:
        seg_diff.append("- Segment contrast not strong today")

    skill_block = "\n".join(
        f"- {k}" for k, _ in skills.most_common(5)
    ) or "- No dominant skill shifts today"

    india_block = (
        "- Budget sensitivity and change management remain key in India\n"
        "- Midcaps likely to adopt before formal governance appears\n"
        "- Expect enablement-heavy roles before pure AI specialist roles"
    )

    writing = (
        "- What Indian midcaps are hiring for that largecaps haven’t formalised yet\n"
        "- Why AI fluency is replacing prompt engineering in Indian teams\n"
        "- How role design is becoming the real AI battleground"
    )

    lab_inputs = (
        "- Exercise: Redesign a role assuming AI as a teammate\n"
        "- Prompt lab: Judgement vs automation trade-offs\n"
        "- Case discussion: Midcap vs largecap AI adoption paths"
    )

    template = Path("DAILY_BRIEF_TEMPLATE.md").read_text(encoding="utf-8")

    brief = (
        template
        .replace("{{date}}", TODAY.isoformat())
        .replace("{{strengthening_themes}}", strengthening)
        .replace("{{segment_differences}}", "\n".join(seg_diff))
        .replace("{{skill_shifts}}", skill_block)
        .replace("{{india_implications}}", india_block)
        .replace("{{writing_angles}}", writing)
        .replace("{{lab_inputs}}", lab_inputs)
    )

    Path(OUTPUT_FILE).write_text(brief, encoding="utf-8")
    print("Daily brief generated")

if __name__ == "__main__":
    main()
