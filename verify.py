#!/usr/bin/env python3
"""Prove the site actually has 1000 unique notes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
NOTES = SITE / "notes"

BANNED = [
    "Open SingLink, Open the World",
    "翻牆",
    "破解",
    "保證 Netflix 4K",
]


def main() -> int:
    pages = [p for p in NOTES.glob("*/index.html") if p.parent.name != "notes"]
    titles = []
    slugs = []
    short = []
    banned_hits = []
    for p in pages:
        text = p.read_text(encoding="utf-8")
        m = re.search(r"<h1>(.*?)</h1>", text, re.S)
        title = re.sub("<.*?>", "", m.group(1)).strip() if m else ""
        titles.append(title)
        slugs.append(p.parent.name)
        # rough text length without tags
        visible = re.sub(r"<script.*?</script>", "", text, flags=re.S)
        visible = re.sub(r"<style.*?</style>", "", visible, flags=re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        words = len(visible.split())
        if words < 80:
            short.append(p.parent.name)
        for b in BANNED:
            if b in text:
                banned_hits.append((p.parent.name, b))

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_notes = sitemap.count("/notes/")
    report = {
        "note_pages": len(pages),
        "unique_titles": len(set(titles)),
        "unique_slugs": len(set(slugs)),
        "short_pages": len(short),
        "banned_hits": banned_hits[:10],
        "has_home": (SITE / "index.html").exists(),
        "has_sitemap": (SITE / "sitemap.xml").exists(),
        "has_robots": (SITE / "robots.txt").exists(),
        "has_howto": (SITE / "how-to" / "index.html").exists(),
        "sitemap_note_entries": sitemap_notes,
        "ok": len(pages) == 1000
        and len(set(titles)) == 1000
        and len(set(slugs)) == 1000
        and not short
        and not banned_hits
        and (SITE / "sitemap.xml").exists(),
    }
    (ROOT / "verify-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
