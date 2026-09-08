# Append parent/child bottom navbars to Quartz content pages.
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"

# Down links from home (path, label)
SECTIONS = [
    ("A-Introduction/index", "Introduction"),
    ("B-Returning-to-active-lifestyle/index", "Returning to an active lifestyle"),
    ("C-Exercise/index", "Exercise"),
    ("D-Nutrition/index", "Nutrition"),
    ("E-Sleep-and-recovery/index", "Sleep and recovery"),
    ("source-catalog", "Source catalog"),
]

# Descriptive Up labels for section indexes
UP_SECTION = {
    "A-Introduction/index": "Introduction (Don't believe everything you read on the internet)",
    "B-Returning-to-active-lifestyle/index": "Returning to an active lifestyle",
    "C-Exercise/index": "Exercise",
    "D-Nutrition/index": "Nutrition",
    "E-Sleep-and-recovery/index": "Sleep and recovery",
}

HOME_UP = ("index", "Stay Capable After 55")

CHILDREN = {
    "A-Introduction/index": [
        ("A-Introduction/S15-fm-7-22-h2f", "FM 7-22"),
        ("A-Introduction/S16-craap-test", "CRAAP Test"),
        ("A-Introduction/S17-adler-how-to-read", "Adler & Van Doren"),
        ("A-Introduction/S01-mckendry-master-athletes", "McKendry et al. (2018)"),
    ],
    "B-Returning-to-active-lifestyle/index": [
        ("B-Returning-to-active-lifestyle/S23-video-cleared-not-ready", "Cleared ≠ ready"),
        ("B-Returning-to-active-lifestyle/S24-video-too-much-too-soon", "Too much too soon"),
        ("B-Returning-to-active-lifestyle/S31-willich-exertion-mi-trigger", "Willich et al. (1993)"),
        ("B-Returning-to-active-lifestyle/S27-acsm-preparticipation-prep", "ACSM prep"),
        ("B-Returning-to-active-lifestyle/S26-podcast-mash-comeback", "Travis Mash podcast"),
    ],
    "C-Exercise/index": [
        ("C-Exercise/S04-fragala-nsca-older-adults", "Fragala et al. (2019)"),
        ("C-Exercise/S02-borde-dose-response", "Borde et al. (2015)"),
        ("C-Exercise/S03-markov-concurrent", "Markov et al. (2023)"),
        ("C-Exercise/S18-currier-acsm-video", "Currier ACSM video"),
        ("C-Exercise/S19-kennerley-velocity-phd", "Kennerley PhD"),
        ("C-Exercise/S09-christensen-solo-training-50", "Christensen"),
        ("C-Exercise/S10-ross-tai-chi-fit-over-60", "Ross / Tai Chi Fit"),
    ],
    "D-Nutrition/index": [
        ("D-Nutrition/S11-desbrow-older-athletes", "Desbrow et al. (2021)"),
        ("D-Nutrition/S28-issn-protein-stand", "ISSN protein stand"),
        ("D-Nutrition/S12-verreijen-protein-weight-loss", "Verreijen et al. (2017)"),
        ("D-Nutrition/S14-trommelen-presleep-protein", "Trommelen & van Loon"),
        ("D-Nutrition/S29-body-signals-elevate-plate", "Elevate Your Plate"),
    ],
    "E-Sleep-and-recovery/index": [
        ("E-Sleep-and-recovery/S13-walsh-athlete-sleep", "Walsh et al. (2021)"),
        ("E-Sleep-and-recovery/S07-sullivan-masters-volume", "Sullivan & Baker"),
        ("E-Sleep-and-recovery/S21-acsm-recovery-older-adults", "ACSM recovery"),
    ],
}

PARENT_BY_CHILD = {}
for section, kids in CHILDREN.items():
    label = UP_SECTION[section]
    for path, _ in kids:
        PARENT_BY_CHILD[path] = (section, label)


def wiki(path: str, label: str) -> str:
    return f"[[{path}|{label}]]"


def format_nav(up, downs) -> str:
    lines = ["", "---", ""]
    if up:
        lines.append(f"**Up:** {wiki(*up)}")
    if downs:
        joined = " · ".join(wiki(p, lab) for p, lab in downs)
        if up:
            lines.append("")
        lines.append(f"**Down:** {joined}")
    lines.append("")
    return "\n".join(lines)


def strip_existing_nav(text: str) -> str:
    marker = "\n---\n\n**Up:**"
    marker2 = "\n---\n\n**Down:**"
    for m in (marker, marker2):
        idx = text.rfind(m)
        if idx != -1:
            tail = text[idx:]
            if "**Up:**" in tail[:80] or "**Down:**" in tail[:80]:
                return text[:idx].rstrip() + "\n"
    return text.rstrip() + "\n"


def nav_for(rel: str):
    if rel == "index":
        return None, SECTIONS
    if rel == "source-catalog":
        return HOME_UP, None
    if rel in CHILDREN:
        return HOME_UP, CHILDREN[rel]
    if rel in PARENT_BY_CHILD:
        return PARENT_BY_CHILD[rel], None
    return None, None


def main():
    updated = []
    for path in sorted(ROOT.rglob("*.md")):
        if "_templates" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        key = rel[:-3] if rel.endswith(".md") else rel
        up, downs = nav_for(key)
        if up is None and not downs:
            continue
        text = strip_existing_nav(path.read_text(encoding="utf-8"))
        path.write_text(text.rstrip() + "\n" + format_nav(up, downs), encoding="utf-8", newline="\n")
        updated.append(key)
    print(f"Updated {len(updated)} pages")
    for u in updated:
        print(" ", u)


if __name__ == "__main__":
    main()
