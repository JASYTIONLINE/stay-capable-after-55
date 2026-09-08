"""Expand acronyms on first use per page: Full Name (ACRONYM)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"

# (bare acronym regex, full expansion, optional full-name-without-paren regex to attach (ACRONYM))
# If full name without paren appears before bare acronym, insert (ACRONYM) after that name instead.
EXPANSIONS: list[tuple[str, str, str | None]] = [
    (r"\bFM\s*7-22\b", "Field Manual (FM) 7-22", r"\bField Manual\s+7-22\b"),
    (r"\bH2F\b", "Holistic Health and Fitness (H2F)", r"\bHolistic Health and Fitness\b"),
    (
        r"\bACSM\b",
        "American College of Sports Medicine (ACSM)",
        r"\bAmerican College of Sports Medicine\b",
    ),
    (
        r"\bNSCA\b",
        "National Strength and Conditioning Association (NSCA)",
        r"\bNational Strength and Conditioning Association\b",
    ),
    (
        r"\bISSN\b",
        "International Society of Sports Nutrition (ISSN)",
        r"\bInternational Society of Sports Nutrition\b",
    ),
    (
        r"\bCRAAP\b",
        "Currency, Relevance, Authority, Accuracy, Purpose (CRAAP)",
        r"\bCurrency,\s*Relevance,\s*Authority,\s*Accuracy,\s*(?:and\s*)?Purpose\b",
    ),
    (
        r"\bBJSM\b",
        "British Journal of Sports Medicine (BJSM)",
        r"\bBritish Journal of Sports Medicine\b",
    ),
    (
        r"\bNEJM\b",
        "New England Journal of Medicine (NEJM)",
        r"\bNew England Journal of Medicine\b",
    ),
    (r"\bCGM\b", "continuous glucose monitor (CGM)", r"\bcontinuous glucose monitors?\b"),
    (r"\bRCT\b", "randomized controlled trial (RCT)", r"\brandomized controlled trials?\b"),
    (
        r"\bYMAA\b",
        "Yang's Martial Arts Association (YMAA)",
        r"\bYang'?s Martial Arts Association\b",
    ),
    (r"\bS&C\b", "strength and conditioning (S&C)", None),  # do not attach inside NSCA name
    (r"\bPhD\b", "Doctor of Philosophy (PhD)", r"\bDoctor of Philosophy\b"),
    (r"\b1SG\b", "First Sergeant (1SG)", r"\bFirst Sergeant\b"),
    (r"\bRD\b", "registered dietitian (RD)", r"\bregistered dietitians?\b"),
    (r"\bMI\b", "myocardial infarction (MI)", r"\bmyocardial infarctions?\b"),
    (r"\bRT\b", "resistance training (RT)", r"\bresistance training\b"),
    (r"\bPRs\b", "personal records (PRs)", r"\bpersonal records\b"),
    (r"\bPR\b", "personal record (PR)", r"\bpersonal records?\b"),
    (r"\bPT\b", "Physical Training (PT)", r"\bPhysical Training\b"),
]


def already_has_paren_form(text: str, expansion: str) -> bool:
    # e.g. expansion ends with (ACSM) — detect that parenthetical intro already present
    m = re.search(r"\(([^)]+)\)\s*$", expansion)
    if not m:
        return False
    acro = m.group(1)
    # Full expansion already present
    if expansion in text:
        return True
    # Or "Something (ACRO)" already there with same acronym token
    return bool(re.search(rf"\({re.escape(acro)}\)", text))


def expand_file(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    for bare_re, expansion, full_name_re in EXPANSIONS:
        if already_has_paren_form(text, expansion):
            continue

        bare_m = re.search(bare_re, text)
        full_m = re.search(full_name_re, text, flags=re.IGNORECASE) if full_name_re else None

        # Prefer attaching (ACRONYM) to an earlier spelled-out name
        if full_m and (bare_m is None or full_m.start() <= bare_m.start()):
            # Don't double-attach if already followed by (
            after = text[full_m.end() : full_m.end() + 10]
            if after.lstrip().startswith("("):
                continue
            acro = re.search(r"\(([^)]+)\)\s*$", expansion)
            insert = f" ({acro.group(1)})" if acro else ""
            # Special case FM 7-22: full name path uses Field Manual 7-22 -> Field Manual (FM) 7-22
            if bare_re.startswith(r"\bFM"):
                text = text[: full_m.start()] + expansion + text[full_m.end() :]
                changes.append(f"{full_m.group(0)} -> {expansion}")
            else:
                text = text[: full_m.end()] + insert + text[full_m.end() :]
                changes.append(f"{full_m.group(0)} + {insert.strip()}")
            continue

        if bare_m:
            # Skip if this match is only the parenthetical acronym already
            start, end = bare_m.start(), bare_m.end()
            if start > 0 and text[start - 1] == "(" and end < len(text) and text[end : end + 1] == ")":
                continue
            text = text[:start] + expansion + text[end:]
            changes.append(f"{bare_m.group(0)} -> {expansion}")

    return text, changes


def main() -> None:
    total = 0
    for path in sorted(ROOT.rglob("*.md")):
        if "_templates" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        updated, changes = expand_file(original)
        if changes and updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"{path.relative_to(ROOT).as_posix()}:")
            for c in changes:
                print(f"  {c}")
            total += len(changes)
    print(f"\nTotal expansions: {total}")


if __name__ == "__main__":
    main()
