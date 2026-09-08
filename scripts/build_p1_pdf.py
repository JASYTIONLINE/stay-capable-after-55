"""Build P1 submission PDF (+ synced txt backup) from the Quartz vault."""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "stay-capable-after-55" / "content"
OUT_DIR = ROOT / "module-05"
PDF_PATH = OUT_DIR / "barkle-p1-curated-collection.pdf"
TXT_PATH = OUT_DIR / "barkle-p1-curated-collection.txt"
PUBLIC_URL = "https://jasyti.com/stay-capable-after-55/"

# Guided-path order (matches section indexes)
SECTIONS: list[tuple[str, str, list[str]]] = [
    (
        "A. Introduction",
        "Doctrine frame (FM 7-22) plus tools to judge claims, plus a still-training research example.",
        [
            "A-Introduction/S15-fm-7-22-h2f.md",
            "A-Introduction/S16-craap-test.md",
            "A-Introduction/S17-adler-how-to-read.md",
            "A-Introduction/S01-mckendry-master-athletes.md",
        ],
    ),
    (
        "B. Returning to an active lifestyle",
        "Comeback preparation after layoff or injury — clearance is not capacity.",
        [
            "B-Returning-to-active-lifestyle/S24-video-too-much-too-soon.md",
            "B-Returning-to-active-lifestyle/S23-video-cleared-not-ready.md",
            "B-Returning-to-active-lifestyle/S31-willich-exertion-mi-trigger.md",
            "B-Returning-to-active-lifestyle/S27-acsm-preparticipation-prep.md",
            "B-Returning-to-active-lifestyle/S26-podcast-mash-comeback.md",
        ],
    ),
    (
        "C. Exercise",
        "Activity pillar: programming standards, concurrent training, and lived practice.",
        [
            "C-Exercise/S04-fragala-nsca-older-adults.md",
            "C-Exercise/S02-borde-dose-response.md",
            "C-Exercise/S03-markov-concurrent.md",
            "C-Exercise/S18-currier-acsm-video.md",
            "C-Exercise/S19-kennerley-velocity-phd.md",
            "C-Exercise/S09-christensen-solo-training-50.md",
            "C-Exercise/S10-ross-tai-chi-fit-over-60.md",
        ],
    ),
    (
        "D. Nutrition",
        "Fuel for capacity — protein, intake structure, and timing under training.",
        [
            "D-Nutrition/S11-desbrow-older-athletes.md",
            "D-Nutrition/S28-issn-protein-stand.md",
            "D-Nutrition/S12-verreijen-protein-weight-loss.md",
            "D-Nutrition/S14-trommelen-presleep-protein.md",
            "D-Nutrition/S29-body-signals-elevate-plate.md",
        ],
    ),
    (
        "E. Sleep and recovery",
        "Sleep, load honesty, and recovery habits that protect progress.",
        [
            "E-Sleep-and-recovery/S13-walsh-athlete-sleep.md",
            "E-Sleep-and-recovery/S07-sullivan-masters-volume.md",
            "E-Sleep-and-recovery/S21-acsm-recovery-older-adults.md",
        ],
    ),
]


def strip_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[\[[^\]]*\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def parse_note(path: Path) -> dict[str, str]:
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^#\s+(.+)$", raw, re.M)
    type_m = re.search(r"\*\*Type:\*\*\s*(.+)", raw)
    cat_m = re.search(r"\*\*Category:\*\*\s*(.+)", raw)
    cite_m = re.search(r"## Citation\n\n(.+?)(?=\n## |\n---\n|$)", raw, re.S)
    ann_m = re.search(r"## Annotation\n\n(.+?)(?=\n## |\n---\n|$)", raw, re.S)
    sid = path.stem.split("-")[0]
    return {
        "id": sid,
        "title": strip_md(title_m.group(1) if title_m else path.stem),
        "type": strip_md(type_m.group(1) if type_m else ""),
        "category": strip_md(cat_m.group(1) if cat_m else ""),
        "citation": strip_md(cite_m.group(1) if cite_m else ""),
        "annotation": strip_md(ann_m.group(1) if ann_m else ""),
    }


def intro_text() -> str:
    raw = (VAULT / "index.md").read_text(encoding="utf-8")
    m = re.search(r"## Introduction\n\n(.+?)(?=\n### Guided path|\n---\n|$)", raw, re.S)
    body = strip_md(m.group(1) if m else "")
    # Drop the "sections below..." line if present; PDF has its own organization note
    lines = [ln for ln in body.splitlines() if "sections below move" not in ln.lower()]
    return "\n".join(lines).strip()


def synthesis_text() -> str:
    """Conclusion from source-catalog.md — What these sources say together."""
    raw = (VAULT / "source-catalog.md").read_text(encoding="utf-8")
    m = re.search(
        r"## What these sources say together\n\n(.+?)(?=\n## Resource Index|\n---\n|$)",
        raw,
        re.S,
    )
    return strip_md(m.group(1) if m else "")


def collect_sources() -> list[tuple[str, str, list[dict[str, str]]]]:
    out = []
    for title, blurb, files in SECTIONS:
        notes = [parse_note(VAULT / rel) for rel in files]
        out.append((title, blurb, notes))
    return out


def build_txt(sections: list[tuple[str, str, list[dict[str, str]]]]) -> str:
    total = sum(len(n) for _, _, n in sections)
    lines: list[str] = []
    lines.append("CMPA 4301 — PROJECT 01: CURATED COLLECTION (PDF BACKUP)")
    lines.append("=" * 56)
    lines.append("Title: Stay Capable After 55")
    lines.append("Subtitle: Strength and conditioning for athletes who remain active after 55")
    lines.append("Curator: 1SG John Barkle")
    lines.append("Course: Systems and Methods of Information Organization and Management (Fall 2026)")
    lines.append("")
    lines.append(f"Public URL (live collection): {PUBLIC_URL}")
    lines.append("")
    lines.append("Purpose of this file:")
    lines.append("  Plain-text / PDF backup of the curated collection for Canvas if the")
    lines.append("  online site is temporarily offline. Open the public URL for full navigation.")
    lines.append("")
    lines.append(f"Status: READY FOR SUBMIT — {total} annotated sources; guided path A–E")
    lines.append("")
    lines.append("=" * 80)
    lines.append("INTRODUCTION")
    lines.append("=" * 80)
    lines.append("")
    lines.append(intro_text())
    lines.append("")
    lines.append("Guided path:")
    lines.append("  A. Introduction")
    lines.append("  B. Returning to an active lifestyle")
    lines.append("  C. Exercise")
    lines.append("  D. Nutrition")
    lines.append("  E. Sleep and recovery")
    lines.append("")
    lines.append("=" * 80)
    lines.append("HOW THIS BACKUP IS ORGANIZED")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Annotations follow the online collection. Each entry includes category,")
    lines.append("type, citation (with URL when available), and a 100–200 word annotation")
    lines.append("covering what the source covers, why it is valuable, who would find it")
    lines.append("useful, and limitations or caveats.")
    lines.append("")

    n = 0
    for section, blurb, notes in sections:
        lines.append("=" * 80)
        lines.append(section)
        lines.append("=" * 80)
        lines.append(blurb)
        lines.append("")
        for note in notes:
            n += 1
            lines.append("-" * 80)
            lines.append(f"SOURCE {n} of {total}  |  {note['id']}  |  {note['title']}")
            lines.append("-" * 80)
            lines.append(f"Category: {note['category']}")
            lines.append(f"Type: {note['type']}")
            lines.append("")
            lines.append("Citation:")
            for cl in note["citation"].splitlines():
                lines.append(f"  {cl}" if cl.strip() else "")
            lines.append("")
            lines.append("Annotation:")
            lines.append(note["annotation"])
            lines.append("")

    lines.append("=" * 80)
    lines.append("CONCLUSION — WHAT THESE SOURCES SAY TOGETHER")
    lines.append("=" * 80)
    lines.append("")
    lines.append(synthesis_text())
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF BACKUP")
    lines.append(f"Live collection: {PUBLIC_URL}")
    lines.append("=" * 80)
    lines.append("")
    return "\n".join(lines)


def build_pdf(sections: list[tuple[str, str, list[dict[str, str]]]]) -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=16,
        leading=20,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "SubCustom",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    meta = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        spaceAfter=3,
        alignment=TA_CENTER,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=13,
        leading=16,
        spaceBefore=14,
        spaceAfter=8,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "BodyJust",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        spaceAfter=4,
        alignment=TA_LEFT,
    )

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Stay Capable After 55 — Curated Collection (PDF Backup)",
        author="1SG John Barkle",
    )
    story: list = []
    total = sum(len(n) for _, _, n in sections)

    story.append(Paragraph(esc("CMPA 4301 — Project 01: Curated Collection"), meta))
    story.append(Paragraph(esc("Stay Capable After 55"), title))
    story.append(
        Paragraph(
            esc("Strength and conditioning for athletes who remain active after 55"),
            subtitle,
        )
    )
    story.append(Paragraph(esc("Curator: 1SG John Barkle"), meta))
    story.append(
        Paragraph(
            esc("Systems and Methods of Information Organization and Management (Fall 2026)"),
            meta,
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            f'<b>Public URL:</b> <link href="{PUBLIC_URL}">{esc(PUBLIC_URL)}</link>',
            body,
        )
    )
    story.append(
        Paragraph(
            esc(
                f"PDF backup for Canvas submission if the live site is offline. "
                f"{total} annotated sources. Prefer the live URL for full navigation."
            ),
            small,
        )
    )

    story.append(Paragraph(esc("Introduction"), h1))
    for para in intro_text().split("\n\n"):
        if para.strip():
            story.append(Paragraph(esc(para.strip()), body))

    story.append(Paragraph(esc("Guided path"), h2))
    for item in [
        "A. Introduction",
        "B. Returning to an active lifestyle",
        "C. Exercise",
        "D. Nutrition",
        "E. Sleep and recovery",
    ]:
        story.append(Paragraph(esc(f"• {item}"), small))

    story.append(PageBreak())
    n = 0
    for section, blurb, notes in sections:
        story.append(Paragraph(esc(section), h1))
        story.append(Paragraph(esc(blurb), small))
        for note in notes:
            n += 1
            story.append(
                Paragraph(
                    esc(f"Source {n} of {total} — {note['id']}: {note['title']}"),
                    h2,
                )
            )
            if note["category"]:
                story.append(Paragraph(esc(f"Category: {note['category']}"), small))
            if note["type"]:
                story.append(Paragraph(esc(f"Type: {note['type']}"), small))
            story.append(Paragraph(esc("Citation"), small))
            for cl in note["citation"].splitlines():
                if cl.strip():
                    story.append(Paragraph(esc(cl.strip()), small))
            story.append(Paragraph(esc("Annotation"), small))
            story.append(Paragraph(esc(note["annotation"]), body))
            story.append(Spacer(1, 6))

    story.append(PageBreak())
    story.append(Paragraph(esc("Conclusion — What these sources say together"), h1))
    for para in synthesis_text().split("\n\n"):
        if para.strip():
            story.append(Paragraph(esc(para.strip()), body))

    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            f'End of backup. Live collection: <link href="{PUBLIC_URL}">{esc(PUBLIC_URL)}</link>',
            meta,
        )
    )
    doc.build(story)


def main() -> None:
    sections = collect_sources()
    txt = build_txt(sections)
    TXT_PATH.write_text(txt, encoding="utf-8", newline="\n")
    build_pdf(sections)
    total = sum(len(n) for _, _, n in sections)
    print(f"Wrote {TXT_PATH}")
    print(f"Wrote {PDF_PATH}")
    print(f"Sources: {total}")
    print(f"PDF size: {PDF_PATH.stat().st_size} bytes")


if __name__ == "__main__":
    main()
