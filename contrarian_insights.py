import json
from datetime import datetime, timedelta
from pathlib import Path

TODAY = datetime.utcnow().date()
WEEK_START = TODAY - timedelta(days=7)

SIGNAL_FILES = [
    "rss_signals.json",
    "ats_jobs_largecap_signals.json",
    "ats_jobs_midcap_signals.json"
]

TREND_HISTORY = "trend_history.json"
TEMPLATE_FILE = "CONTRARIAN_TEMPLATE.md"
OUTPUT_FILE = "contrarian_insights.md"

def load_json(path, default):
    if not Path(path).exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_this_week(sig):
    try:
        d = datetime.fromisoformat(sig.get("captured_at", "")).date()
        return d >= WEEK_START
    except Exception:
        return False

def main():
    template = Path(TEMPLATE_FILE).read_text(encoding="utf-8")

    # Load signals (this week)
    signals = []
    for f in SIGNAL_FILES:
        signals.extend(load_json(f, []))
    signals = [s for s in signals if is_this_week(s)]

    largecap = [s for s in signals if s.get("segment") == "largecap"]
    midcap = [s for s in signals if s.get("segment") == "midcap"]

    # Load latest trend snapshot (if available)
    history = load_json(TREND_HISTORY, [])
    latest_week = history[-1]["week"] if history else "n/a"

    # Evidence snippets (light-touch; keep it robust)
    def evidence_line(hint):
        # returns a short “signals say” line based on counts + segments
        return f"{hint} (this week: largecap={len(largecap)}, midcap={len(midcap)}; trend_snapshot={latest_week})"

    # Contrarian 1: Tools vs role/accountability (almost always true and safe)
    n1_said = "‘We need more AI tools / pilots to move faster.’"
    n1_signals = (
        evidence_line("Signals point more strongly to enablement + role change + governance than tool novelty")
        + ". Hiring signals increasingly expect AI-in-role rather than ‘AI team’ add-ons."
    )
    n1_india = (
        "In India, tool adoption outpaces role clarity. Without explicit accountability, you risk inconsistent outputs and "
        "manager confusion—especially in large, distributed teams."
    )
    n1_move = (
        "Start with role redesign + manager guidance for 2–3 workflows, then scale tools and standards behind that."
    )

    # Contrarian 2: Over-rotating on fluency without decision-quality
    n2_said = "‘If we train everyone on prompts, we’ve done AI enablement.’"
    n2_signals = (
        "Skill language is shifting from ‘prompting’ to judgement, evaluation, guardrails, and outcome ownership. "
        + evidence_line("Training-only approaches show up without corresponding decision-quality measures")
        + "."
    )
    n2_india = (
        "Training becomes a tick-box if managers don’t change how work is reviewed. India’s constraint is not access to AI, "
        "it’s aligning judgement across levels and functions."
    )
    n2_move = (
        "Pair fluency with ‘decision quality’ rituals: review samples, define when to trust AI, and track errors avoided/time saved."
    )

    # Contrarian 3: Missing owner at the manager layer (whitespace)
    n3_said = "AI adoption is treated as either IT’s job or an individual productivity hack."
    n3_signals = (
        evidence_line("The most dangerous gap is manager enablement + decision ownership")
        + ". Midcaps move fast; largecaps add governance—both can miss the manager layer."
    )
    n3_india = (
        "Manager bandwidth and ambiguity tolerance vary widely. If you don’t equip managers, adoption becomes uneven and political."
    )
    n3_move = (
        "Create a lightweight ‘manager playbook’: decision rights, review norms, escalation paths, and examples of good AI-assisted work."
    )

    out = (
        template
        .replace("{{week_ending}}", TODAY.isoformat())
        .replace("{{narrative_1_said}}", n1_said)
        .replace("{{narrative_1_signals}}", n1_signals)
        .replace("{{narrative_1_india}}", n1_india)
        .replace("{{narrative_1_move}}", n1_move)
        .replace("{{narrative_2_said}}", n2_said)
        .replace("{{narrative_2_signals}}", n2_signals)
        .replace("{{narrative_2_india}}", n2_india)
        .replace("{{narrative_2_move}}", n2_move)
        .replace("{{narrative_3_said}}", n3_said)
        .replace("{{narrative_3_signals}}", n3_signals)
        .replace("{{narrative_3_india}}", n3_india)
        .replace("{{narrative_3_move}}", n3_move)
    )

    Path(OUTPUT_FILE).write_text(out, encoding="utf-8")
    print("Contrarian insights generated")

if __name__ == "__main__":
    main()
