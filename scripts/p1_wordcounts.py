from pathlib import Path
import re

root = Path(r"c:\lt-c-files\shared-files\08-github\r-4301-online-management\stay-capable-after-55\content")


def words(text: str) -> int:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[\[[^\]]*\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    return len(re.findall(r"[A-Za-z0-9']+", text))


idx = (root / "index.md").read_text(encoding="utf-8")
m = re.search(r"## Introduction\n\n(.*?)### Guided path", idx, re.S)
intro = m.group(1) if m else ""
print("INTRO_WORDS", words(intro))

stats = []
for p in sorted(root.rglob("S*.md")):
    if "_templates" in p.parts:
        continue
    t = p.read_text(encoding="utf-8")
    am = re.search(r"## Annotation\n\n(.*?)(\n## |\n---\n|$)", t, re.S)
    if not am:
        continue
    typ = re.search(r"\*\*Type:\*\*\s*(.+)", t)
    w = words(am.group(1))
    stats.append((w, p.name, typ.group(1).strip() if typ else "?"))

print("SOURCE_COUNT", len(stats))
print("UNDER_100", [(n, w) for w, n, _ in stats if w < 100])
print("OVER_200", [(n, w) for w, n, _ in stats if w > 200])
print("MIN_MAX", min(w for w, _, _ in stats), max(w for w, _, _ in stats))
for w, n, t in sorted(stats):
    flag = " LOW" if w < 100 else (" HIGH" if w > 200 else "")
    print(f"{w:3d}{flag}  {n}  |  {t}")
