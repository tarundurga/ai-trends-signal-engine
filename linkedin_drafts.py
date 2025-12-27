from datetime import datetime
from pathlib import Path

TODAY = datetime.utcnow().date()

TEMPLATE_FILE = "LINKEDIN_DRAFTS_TEMPLATE.md"
OUTPUT_FILE = "linkedin_drafts.md"

# Inputs we already generate
CXO_FILE = "weekly_cxo_synthesis.md"
CONTRA_FILE = "contrarian_insights.md"

def safe_read(path):
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")

def extract_section(text, heading):
    """
    Minimal section extractor: grabs text after a heading until next heading.
    Assumes Markdown headings like '## 3. ...'
    """
    if not text:
        return ""
    idx = text.find(heading)
    if idx == -1:
        return ""
    rest = text[idx + len(heading):]
    # stop at next '## ' heading
    next_idx = rest.find("\n## ")
    chunk = rest[:next_idx] if next_idx != -1 else rest
    return chunk.strip()

def main():
    template = Path(TEMPLATE_FILE).read_text(encoding="utf-8")
    cxo = safe_read(CXO_FILE)
    contra = safe_read(CONTRA_FILE)

    # Pull useful raw material
    divergence = extract_section(cxo, "## 3. Largecap vs Midcap: how strategies are diverging")
    whitespace = extract_section(cxo, "## 6. Emerging whitespace opportunities to consider")
    planning = extract_section(cxo, "## 8. How this feeds next-quarter planning")
    # Contrarian items are already concise; just take first section-ish
    contra_1 = extract_section(contra, "## 1) The “false obvious” narrative") or contra[:800]

    # Draft 1 (CXO)
    cxo_hook = "Most AI strategies are still tool strategies. That’s the wrong unit of change."
    cxo_body = (
        "What’s emerging more clearly is this: AI adoption is becoming a *work design* problem.\n\n"
        "Two patterns are diverging:\n"
        f"{divergence}\n\n"
        "And a repeatable whitespace shows up across both:\n"
        f"{whitespace}\n\n"
        "If you’re planning next quarter, the safest first move is to redesign a few roles and manager rituals — "
        "then scale tools behind that.\n\n"
        f"{planning}"
    ).strip()

    cxo_close = "If you had to pick one place to start: manager enablement or role redesign — which would you choose, and why?"

    # Draft 2 (Designer/creator)
    design_hook = "AI won’t replace creative work. It will replace *unclear craft*."
    design_body = (
        "The most interesting shift isn’t new tools — it’s how the definition of ‘good work’ is changing.\n\n"
        "When AI becomes a collaborator, craft moves upstream:\n"
        "- clearer intent\n"
        "- better judgement\n"
        "- stronger taste\n"
        "- tighter feedback loops\n\n"
        "That means designers, writers, strategists, and creators need to focus less on output volume and more on:\n"
        "- framing problems well\n"
        "- asking better questions\n"
        "- reviewing and refining with discipline\n"
        "- knowing what should *not* be delegated\n\n"
        "In India, this matters because teams are large, time is scarce, and ambiguity is everywhere. "
        "The creator advantage will go to people who can consistently produce clarity."
    ).strip()

    design_close = "What part of your craft have you already started protecting from AI — and what part have you happily delegated?"

    # Draft 3 (Contrarian)
    contra_hook = "A quiet risk: ‘AI fluency’ programmes that don’t change how decisions are made."
    contra_body = (
        "A lot of organisations are optimising for training completion and tool usage.\n\n"
        "But the real question is: are decisions getting better?\n\n"
        f"{contra_1}\n\n"
        "In practice, this means pairing AI fluency with simple decision-quality rituals:\n"
        "- define when AI output needs review\n"
        "- track errors avoided and time saved\n"
        "- make accountability explicit\n\n"
        "Otherwise AI becomes noise — amplified at speed."
    ).strip()

    contra_close = "If you run enablement: do you measure adoption, or decision quality — and why?"

    out = (
        template
        .replace("{{week_ending}}", TODAY.isoformat())
        .replace("{{cxo_hook}}", cxo_hook)
        .replace("{{cxo_body}}", cxo_body)
        .replace("{{cxo_close}}", cxo_close)
        .replace("{{design_hook}}", design_hook)
        .replace("{{design_body}}", design_body)
        .replace("{{design_close}}", design_close)
        .replace("{{contra_hook}}", contra_hook)
        .replace("{{contra_body}}", contra_body)
        .replace("{{contra_close}}", contra_close)
    )

    Path(OUTPUT_FILE).write_text(out, encoding="utf-8")
    print("LinkedIn drafts generated")

if __name__ == "__main__":
    main()
