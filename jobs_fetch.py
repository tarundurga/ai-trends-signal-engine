import json
import re
from datetime import datetime
import requests
from pathlib import Path

TARGET_FILES = [
    ("ats_targets_largecap.json", "ats_jobs_largecap_signals.json"),
    ("ats_targets_midcap.json", "ats_jobs_midcap_signals.json"),
]

AI_KEYWORDS = [
    "genai", "generative ai", "llm", "copilot", "prompt",
    "agent", "agents", "orchestration", "rag", "retrieval",
    "machine learning", "ml", "artificial intelligence", "ai",
    "automation", "data", "analytics"
]

SKILL_PATTERNS = [
    r"\bprompt\b", r"\bprompts\b", r"\bllm\b", r"\bllms\b",
    r"\brag\b", r"\bagents?\b", r"\bevaluation\b", r"\bguardrails?\b",
    r"\bgovernance\b", r"\bmodel risk\b", r"\bresponsible ai\b",
    r"\bpython\b", r"\bsql\b", r"\bpower bi\b", r"\btableau\b",
    r"\bchange management\b", r"\btraining\b", r"\benablement\b",
    r"\bproduct management\b", r"\bux\b", r"\bdesign\b"
]

INDIA_LOC_HINTS = ["india", "bengaluru", "bangalore", "mumbai", "gurgaon", "gurugram", "noida", "hyderabad", "pune", "chennai", "kolkata", "ahmedabad"]

def contains_ai(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in AI_KEYWORDS)

def extract_skill_hits(text: str):
    t = (text or "").lower()
    hits = []
    for pat in SKILL_PATTERNS:
        if re.search(pat, t):
            hits.append(pat.strip("\\b"))
    return sorted(set(hits))

def safe_get(url, timeout=25):
    return requests.get(url, timeout=timeout, headers={"User-Agent": "ai-trends-signal-engine/1.0"})

def fetch_greenhouse(board_url):
    token = board_url.rstrip("/").split("/")[-1]
    api = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    r = safe_get(api)
    r.raise_for_status()
    return r.json().get("jobs", [])

def fetch_lever(api_url):
    r = safe_get(api_url)
    r.raise_for_status()
    return r.json()

def india_flags(location: str):
    loc = (location or "").lower()
    is_india = any(h in loc for h in INDIA_LOC_HINTS)
    return ("India" if is_india else "Global", "High" if is_india else "Medium")

def normalise_job(company, segment, source, job):
    title = job.get("title") or ""
    # Greenhouse location format differs from Lever; handle both
    location = ""
    if isinstance(job.get("location"), dict):
        location = job.get("location", {}).get("name", "")
    else:
        location = (job.get("categories", {}) or {}).get("location", "") or ""

    url = job.get("absolute_url") or job.get("hostedUrl") or job.get("applyUrl") or ""
    description = job.get("content") or job.get("descriptionPlain") or job.get("description") or ""
    team = ""
    if isinstance(job.get("departments"), list) and job.get("departments"):
        team = job.get("departments")[0].get("name", "")
    else:
        team = (job.get("categories", {}) or {}).get("team", "") or ""

    created_at = job.get("updated_at") or job.get("createdAt") or job.get("created_at") or ""

    text_blob = f"{title}\n{team}\n{location}\n{description}"
    geo_primary, india_relevance = india_flags(location)

    return {
        "captured_at": datetime.utcnow().isoformat(),
        "segment": segment,                 # <-- key addition
        "source_channel": "ats_jobs",
        "source_type": "job_posting",
        "geo_primary": geo_primary,
        "india_relevance": india_relevance,
        "org_name": company,
        "industry": "",
        "role_or_skill_hint": "",
        "title": title,
        "snippet": (re.sub(r"\s+", " ", description).strip()[:300] if description else ""),
        "link": url,
        "evidence_weight": 5,
        "notes": f"{source}; location={location}; team={team}; created_at={created_at}",
        "skill_hits": extract_skill_hits(text_blob),
        "ai_related": contains_ai(text_blob)
    }

def process_targets(target_file: str, output_file: str):
    if not Path(target_file).exists():
        print(f"Missing {target_file}, skipping.")
        return

    with open(target_file, "r", encoding="utf-8") as f:
        targets = json.load(f)

    segment = targets.get("segment", "unknown")
    all_signals = []

    for t in targets.get("greenhouse", []):
        company = t["name"]
        board_url = t["board_url"]
        try:
            jobs = fetch_greenhouse(board_url)
            for job in jobs:
                sig = normalise_job(company, segment, "greenhouse", job)
                if sig["ai_related"]:
                    all_signals.append(sig)
        except Exception as e:
            all_signals.append({
                "captured_at": datetime.utcnow().isoformat(),
                "segment": segment,
                "source_channel": "ats_jobs",
                "source_type": "error",
                "geo_primary": "Global",
                "india_relevance": "Low",
                "org_name": company,
                "industry": "",
                "role_or_skill_hint": "",
                "title": "ERROR fetching Greenhouse jobs",
                "snippet": str(e)[:300],
                "link": board_url,
                "evidence_weight": 1,
                "notes": "greenhouse fetch error"
            })

    for t in targets.get("lever", []):
        company = t["name"]
        api_url = t["api_url"]
        try:
            jobs = fetch_lever(api_url)
            for job in jobs:
                sig = normalise_job(company, segment, "lever", job)
                if sig["ai_related"]:
                    all_signals.append(sig)
        except Exception as e:
            all_signals.append({
                "captured_at": datetime.utcnow().isoformat(),
                "segment": segment,
                "source_channel": "ats_jobs",
                "source_type": "error",
                "geo_primary": "Global",
                "india_relevance": "Low",
                "org_name": company,
                "industry": "",
                "role_or_skill_hint": "",
                "title": "ERROR fetching Lever jobs",
                "snippet": str(e)[:300],
                "link": api_url,
                "evidence_weight": 1,
                "notes": "lever fetch error"
            })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_signals, f, indent=2)

    print(f"{segment}: saved {len(all_signals)} AI-related job signals -> {output_file}")

def main():
    for target_file, output_file in TARGET_FILES:
        process_targets(target_file, output_file)

if __name__ == "__main__":
    main()
