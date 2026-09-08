"""HTTP-check outbound citation/org URLs used in content notes."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"
UA = "Mozilla/5.0 (compatible; stay-capable-link-check/1.0)"

SKIP_PREFIXES = (
    "https://doi.org/",  # often blocks bots; still usually fine for readers
)


def extract_urls(text: str) -> set[str]:
    urls = set(re.findall(r"https?://[^\s\)\]\>\"']+", text))
    cleaned = set()
    for u in urls:
        u = u.rstrip(".,;:)")
        cleaned.add(u)
    return cleaned


def check(url: str) -> tuple[str, int | str]:
    if url.startswith(SKIP_PREFIXES):
        return "skip-doi", "n/a"
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return "ok", resp.status
    except urllib.error.HTTPError as e:
        # Some hosts reject HEAD; try GET
        if e.code in (403, 405, 400):
            try:
                req2 = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
                with urllib.request.urlopen(req2, timeout=15) as resp:
                    return "ok-get", resp.status
            except Exception as e2:
                return "fail", f"{type(e2).__name__}: {e2}"
        return "fail", e.code
    except Exception as e:
        # Retry GET once
        try:
            req2 = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
            with urllib.request.urlopen(req2, timeout=15) as resp:
                return "ok-get", resp.status
        except Exception as e2:
            return "fail", f"{type(e2).__name__}: {e2}"


def main() -> None:
    all_urls: dict[str, list[str]] = {}
    for path in ROOT.rglob("*.md"):
        if "_templates" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for url in extract_urls(text):
            all_urls.setdefault(url, []).append(path.relative_to(ROOT).as_posix())

    print(f"Unique URLs: {len(all_urls)}\n")
    fails = []
    for url in sorted(all_urls):
        status, detail = check(url)
        files = ", ".join(all_urls[url][:3])
        if status.startswith("ok") or status.startswith("skip"):
            print(f"OK  [{status}] {detail}  {url}")
        else:
            print(f"BAD [{status}] {detail}  {url}")
            print(f"    in: {files}")
            fails.append((url, detail, files))

    print(f"\nFailures: {len(fails)}")
    for url, detail, files in fails:
        print(f"- {url}\n  {detail}\n  {files}")


if __name__ == "__main__":
    main()
