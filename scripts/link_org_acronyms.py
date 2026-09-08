"""Wrap first org expansion per page in a markdown link to the org core site.

Handles plain text and first occurrence inside a Quartz wikilink display label.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"

ORG_LINKS: list[tuple[str, str]] = [
    (
        "American College of Sports Medicine (ACSM)",
        "https://www.acsm.org",
    ),
    (
        "National Strength and Conditioning Association (NSCA)",
        "https://www.nsca.com",
    ),
    (
        "International Society of Sports Nutrition (ISSN)",
        "https://www.issn.org",
    ),
    (
        "New England Journal of Medicine (NEJM)",
        "https://www.nejm.org",
    ),
    (
        "British Journal of Sports Medicine (BJSM)",
        "https://bjsm.bmj.com",
    ),
    (
        "Yang's Martial Arts Association (YMAA)",
        "https://ymaa.com",
    ),
    (
        "Holistic Health and Fitness (H2F)",
        "https://www.army.mil/article/239475/holistic_health_added_to_army_fitness_doctrine",
    ),
    (
        "Field Manual (FM) 7-22",
        "https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN44522-FM_7-22-002-WEB-7.pdf",
    ),
    (
        "Currency, Relevance, Authority, Accuracy, Purpose (CRAAP)",
        "https://library.csuchico.edu/sites/default/files/craap-test.pdf",
    ),
]


def already_linked(text: str, phrase: str, url: str) -> bool:
    return f"[{phrase}]({url})" in text


def link_plain(text: str, phrase: str, url: str) -> tuple[str, bool]:
    """Link first plain-text (non-wikilink) occurrence."""
    idx = 0
    while True:
        start = text.find(phrase, idx)
        if start == -1:
            return text, False
        end = start + len(phrase)
        # skip if already markdown-linked
        if text[end : end + 2] == "](":
            idx = end
            continue
        # skip inside wikilink
        open_idx = text.rfind("[[", 0, start)
        close_before = text.rfind("]]", 0, start)
        if open_idx != -1 and close_before < open_idx:
            close_after = text.find("]]", end)
            if close_after != -1:
                idx = end
                continue
        return text[:start] + f"[{phrase}]({url})" + text[end:], True


def link_inside_wikilink(text: str, phrase: str, url: str) -> tuple[str, bool]:
    """If phrase only lives in a wikilink label, hoist org link before the wikilink.

    [[path|...phrase...rest]]  ->  [phrase](url) ([[path|rest]])
    when the label is exactly phrase or phrase + separator + rest.
    """
    # Match wikilinks whose label contains the phrase
    pattern = re.compile(
        r"\[\["
        r"([^\]|]+)"  # path
        r"\|"
        r"([^\]]*?)"  # label
        r"\]\]"
    )
    for m in pattern.finditer(text):
        path, label = m.group(1), m.group(2)
        if phrase not in label:
            continue
        # Build replacement
        if label.strip() == phrase:
            new_label = path.split("/")[-1].replace("-", " ")
            replacement = f"[{phrase}]({url}) ([[{path}|open note]])"
        elif label.startswith(phrase):
            rest = label[len(phrase) :].lstrip(" —–-·|/ ")
            if rest:
                replacement = f"[{phrase}]({url}) ([[{path}|{rest}]])"
            else:
                replacement = f"[{phrase}]({url}) ([[{path}|open note]])"
        else:
            # phrase embedded mid-label — link phrase in prose before wikilink, shorten label
            rest = label.replace(phrase, "").replace("  ", " ").strip(" —–-·|/")
            if rest:
                replacement = f"[{phrase}]({url}) ([[{path}|{rest}]])"
            else:
                replacement = f"[{phrase}]({url}) ([[{path}|open note]])"
        return text[: m.start()] + replacement + text[m.end() :], True
    return text, False


def process(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    for phrase, url in ORG_LINKS:
        if already_linked(text, phrase, url):
            continue
        text2, ok = link_plain(text, phrase, url)
        if ok:
            changes.append(phrase)
            text = text2
            continue
        text2, ok = link_inside_wikilink(text, phrase, url)
        if ok:
            changes.append(phrase + " (from wikilink)")
            text = text2
    return text, changes


def main() -> None:
    total = 0
    for path in sorted(ROOT.rglob("*.md")):
        if "_templates" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        updated, changes = process(original)
        if changes and updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"{path.relative_to(ROOT).as_posix()}:")
            for c in changes:
                print(f"  + {c}")
            total += len(changes)
    print(f"\nTotal org links added this run: {total}")


if __name__ == "__main__":
    main()
