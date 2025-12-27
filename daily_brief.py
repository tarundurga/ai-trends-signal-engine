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

def load_signals():
    signals = []
    for f in FILES:
        if Path(f).exists():
            with open(f, "r", encoding="utf-8") as fh:
                try:
                    signals.extend(json.load(fh))
                except Exception:
                    pass
    return signals

def is_recent(sig):
    try:
        d = datetime.fromisoformat(sig.get("captured_at", "")).date()
        return d >= YESTERDAY
    except Exception:
        return False

def main():
    signals = [s for s in load_signals() if is_recent(s)]

    largecap = [s for s in signals if s.get("segment") == "largecap"]
    midcap = [s for s in signals if s.get("segment") == "midcap"]

    skill_counter = Counter()
    for s in signals:
        for sk in s.get("skill_hits", []):
            skill_counter[sk] += 1

    # -------- Section 1: Strengthening trends --------
    strengthening = (
        "Across today’s signals, there is increasing evidence that AI-related work is shifting "
        "away from isolated experimentation toward more explicit role and capability design. "
        "This is visible through repeated hiring signals and organisational commentary that frame "
        "AI not as a tool to try, but as a capability to be embedded into day-to-day work."
    )

    # -------- Section 2: Largecap vs Midcap divergence --------
    if largecap and midcap:
        segment_diff = (
            f"Large organisations are signalling a need to stabilise and standardise AI adoption. "
            f"Recent largecap job postings ({len(largecap)} signals) emphasise enablement, governance, "
            f"risk management, and structured rollout. AI appears here as an organisational capability.\n\n"
            f"In contrast, mid-sized companies ({len(midcap)} signals) are hiring for speed and leverage. "
            f"Roles are broader, expectations are less formalised, and individuals are expected to "
            f'use AI directly to improve output. AI appears here as a force multiplier rather than a '
            f"managed programme."
        )
    else:
        segment_diff = (
            "Today’s data does not yet show a strong divergence between large and mid-sized organisations. "
            "This often happens early in a trend cycle, before patterns become explicit."
        )

    # -------- Section 3: Skills & role shifts --------
    top_skills = [k for k, _ in skill_counter.most_common(5)]
    if top_skills:
        skill_block = (
            "The most frequently recurring skills across roles point to a clear shift in expectations. "
            f"Instead of narrow technical skills, organisations are looking for combinations such as: "
            f"{', '.join(top_skills)}.\n\n"
            "This suggests that the market is moving away from specialised ‘AI roles’ and towards "
            "redefining existing roles to work effectively with AI — blending judgement, domain context, "
            "and tool fluency."
        )
    else:
        skill_block = (
            "No dominant skill cluster emerged today. This usually indicates either early exploration "
            "or fragmented experimentation across organisations."
        )

    # -------- Section 4: India-specific implications --------
    india_block = (
        "In the Indian context, these shifts carry specific implications. Budget sensitivity, large teams, "
        "and uneven digital maturity mean that AI adoption is more likely to succeed when framed as "
        "enablement rather than replacement.\n\n"
        "Mid-sized Indian companies are likely to adopt AI faster because decision cycles are shorter, "
        "while large organisations will prioritise guardrails and change management. This creates a "
        "window where Indian midcaps may develop practical AI-native ways of working before largecaps "
        "formalise them."
    )

    # -------- Section 5: Writing angles --------
    writing = (
        "- Why Indian midcaps are becoming the testing ground for AI-native roles\n"
        "- The real AI skill shift is not technical — it’s about judgement and context\n"
        "- Large organisations are slowing down AI to make it scale"
    )

    # -------- Section 6: Lab inputs --------
    lab_inputs = (
        "- Exercise: Redesign a current role assuming AI is a collaborator, not a tool\n"
        "- Discussion: Where should judgement remain human as AI capability increases?\n"
        "- Case comparison: Midcap speed vs largecap safety in AI adoption"
    )

    template = Path("DAILY_BRIEF_TEMPLATE.md").read_text(encoding="utf-8")

    brief = (
        template
        .replace("{{date}}", TODAY.isoformat())
        .replace("{{strengthening_themes}}", strengthening)
        .replace("{{segment_differences}}", segment_diff)
        .replace("{{skill_shifts}}", skill_block)
        .replace("{{india_implications}}", india_block)
        .replace("{{writing_angles}}", writing)
        .replace("{{lab_inputs}}", lab_inputs)
    )

    Path("daily_brief.md").write_text(brief, encoding="utf-8")
    print("Daily brief generated (analysis-led)")

if __name__ == "__main__":
    main()
