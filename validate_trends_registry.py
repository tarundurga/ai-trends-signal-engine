import json
import sys
from datetime import datetime

ALLOWED_STATUS = {"emerging", "strengthening", "stable", "weakening", "invalidated"}
ALLOWED_CONF = {"low", "medium", "high"}

REQUIRED_TOP_KEYS = {"meta", "trends"}
REQUIRED_TREND_KEYS = {
    "id",
    "name",
    "status",
    "first_promoted_on",
    "last_reviewed_on",
    "time_horizon",
    "india_translation",
    "summary",
    "promotion_evidence",
}

REQUIRED_EVIDENCE_KEYS = {
    "review_window",
    "evidence_types",
    "evidence_notes",
    "falsifiers",
    "confidence",
}

def _is_iso_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

def main(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    missing_top = REQUIRED_TOP_KEYS - set(data.keys())
    if missing_top:
        print(f"[FAIL] Missing top-level keys: {sorted(missing_top)}")
        return 1

    if not isinstance(data["trends"], list):
        print("[FAIL] 'trends' must be a list.")
        return 1

    errors = []
    for i, t in enumerate(data["trends"]):
        if not isinstance(t, dict):
            errors.append(f"trends[{i}] is not an object")
            continue

        missing = REQUIRED_TREND_KEYS - set(t.keys())
        if missing:
            errors.append(f"trends[{i}] missing keys: {sorted(missing)}")

        status = t.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"trends[{i}] invalid status '{status}' (allowed: {sorted(ALLOWED_STATUS)})")

        for k in ["first_promoted_on", "last_reviewed_on"]:
            v = t.get(k)
            if not isinstance(v, str) or not _is_iso_date(v):
                errors.append(f"trends[{i}] '{k}' must be YYYY-MM-DD")

        pe = t.get("promotion_evidence", {})
        if not isinstance(pe, dict):
            errors.append(f"trends[{i}] promotion_evidence must be an object")
        else:
            missing_pe = REQUIRED_EVIDENCE_KEYS - set(pe.keys())
            if missing_pe:
                errors.append(f"trends[{i}] promotion_evidence missing keys: {sorted(missing_pe)}")

            conf = pe.get("confidence")
            if conf not in ALLOWED_CONF:
                errors.append(f"trends[{i}] promotion_evidence.confidence invalid '{conf}' (allowed: {sorted(ALLOWED_CONF)})")

            fals = pe.get("falsifiers")
            if not isinstance(fals, list) or len(fals) == 0:
                errors.append(f"trends[{i}] promotion_evidence.falsifiers must be a non-empty list")

    if errors:
        print("[FAIL] TRENDS_REGISTRY.json validation failed:")
        for e in errors:
            print(" -", e)
        return 1

    print("[OK] TRENDS_REGISTRY.json is valid.")
    return 0

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "TRENDS_REGISTRY.json"
    raise SystemExit(main(path))
