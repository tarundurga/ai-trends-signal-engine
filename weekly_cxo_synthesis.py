import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

TODAY = datetime.utcnow().date()
WEEK_START = TODAY - timedelta(days=7)

FILES = [
    "rss_signals.json",
    "ats_jobs_largecap_signals.json",
    "ats_jobs_midcap_signals.json"
]

TEMPLATE_FILE = "WEEKLY_CXO_SYNTHESIS_TEMPLATE.md"
OUTPUT_FILE = "weekly_cxo_synthesis.md"

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

def is_this_week(sig):
    try:
        d = datetime.fromisoformat(sig.get("captured_at", "")).date()
        return d >= WEEK_START
    except Exception:
        return False

def main():
    # Ensure template exists
    if not Path(TEMPLATE_FILE).exists():
        raise FileNotFoundError(f"Missing template file: {TEMPLATE_FILE}")

    signals = [s for s in load_signals() if is_this_week(s)]

    largecap = [s for s in signals if s.get("segment") == "largecap"]
    midcap = [s for s in signals if s.get("segment") == "midcap"]

    skill_counter = Counter()
    for s in signals:
        for sk in s.get("skill_hits", []):
            skill_counter[sk] += 1

    # 1) Material change
    material_change = (
        "This week marked a shift from exploratory AI conversations toward more explicit discussions "
        "around how work, roles, and accountability need to change as AI becomes embedded in daily operations."
    )

    # 2) Clarity
    clarity_statement = (
        "It is now clearer that AI adoption is not bottlenecked by technology availability, "
        "but by organisational readiness — particularly role design, decision rights, and manager capability."
    )

    # 3) Segment divergence
    segment_divergence = (
        f"Large organisations ({len(largecap)} signals) are converging on stability and risk management — "
        f"building enablement programs, governance layers, and controlled rollouts.\n\n"
        f"Mid-sized organisations ({len(midcap)} signals) are prioritising speed and leverage, "
        f"expecting individuals to integrate AI directly into their work with minimal formal structure."
    )

    # 4) Skills & roles
    top_skills = [k for k, _ in skill_counter.most_common(6)]
    if top_skills:
        skills_and_roles = (
            "Leaders should begin preparing for hybrid roles that combine domain expertise, judgement, "
            "and AI fluency rather than standalone AI specialists.\n\n"
            f"Recurring skill signals this week include: {', '.join(top_skills)}."
        )
    else:
        skills_and_roles = (
            "No dominant skill cluster emerged this week. This can indicate early exploration or fragmented experimentation."
        )

    # 5) Watchlist
    watchlist = (
        "- Fully autonomous, agent-driven decision systems\n"
        "- Organisation-wide AI mandates without role redesign\n"
        "- Creation of AI-specific roles without clear accountability for outcomes"
    )

    # 6) Whitespace opportunities
    whitespace_opportunities = (
        "Several gaps are becoming visible between intent and execution:\n\n"
        "- **Manager enablement**: Middle management is expected to lead AI adoption, but few organisations are explicitly "
        "building AI judgement and facilitation skills at this layer.\n\n"
        "- **Role transition frameworks**: Organisations talk about reskilling, but lack clear models for how existing roles "
        "evolve when AI becomes a collaborator.\n\n"
        "- **Decision quality metrics**: Tools are measured, but there is limited focus on how AI changes the quality, speed, "
        "and confidence of decisions.\n\n"
        "These represent opportunities to act early — before they become formalised best practices."
    )

    # 7) India implications
    executive_implications = (
        "For Indian CXOs, advantage will come less from which tools are adopted and more from how quickly organisations "
        "redesign roles, decision rights, and manager capability. Midcaps can learn faster; largecaps can institutionalise trust."
    )

    # 8) Planning implications
    planning_implications = (
        "- Pilot manager-focused AI enablement, not just individual training\n"
        "- Redesign 2–3 critical roles assuming AI support\n"
        "- Create explicit forums to clarify decision ownership in AI-assisted work\n"
        "- Treat whitespace initiatives as strategic experiments, not compliance exercises"
    )

    template = Path(TEMPLATE_FILE).read_text(encoding="utf-8")

    synthesis = (
        template
        .replace("{{week_ending}}", TODAY.isoformat())
        .replace("{{material_change}}", material_change)
        .replace("{{clarity_statement}}", clarity_statement)
        .replace("{{segment_divergence}}", segment_divergence)
        .replace("{{skills_and_roles}}", skills_and_roles)
        .replace("{{watchlist}}", watchlist)
        .replace("{{whitespace_opportunities}}", whitespace_opportunities)
        .replace("{{executive_implications}}", executive_implications)
        .replace("{{planning_implications}}", planning_implications)
    )

    Path(OUTPUT_FILE).write_text(synthesis, encoding="utf-8")
    print("Weekly CXO synthesis generated")

if __name__ == "__main__":
    main()

