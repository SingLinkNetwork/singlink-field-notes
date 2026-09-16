#!/usr/bin/env python3
"""Prove 1000 generated mini-sites are unique and crawlable."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "minisites"

BANNED = [
    "Open SingLink, Open the World",
    "翻牆",
    "翻墙",
    "科学上网",
    "破解",
    "保證 Netflix 4K",
]
CHINA_MARKETS = ["mainland China", "中国大陆", "中國大陸", "in China we"]


def visible_text(html: str) -> str:
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def main() -> int:
    dirs = sorted(p for p in OUT.iterdir() if p.is_dir()) if OUT.exists() else []
    titles = []
    bodies = []
    hashes = []
    short = []
    banned_hits = []
    missing = []
    bad_cta = []
    for d in dirs:
        index = d / "index.html"
        if not index.exists():
            missing.append(d.name)
            continue
        text = index.read_text(encoding="utf-8")
        m = re.search(r"<h1>(.*?)</h1>", text, re.S)
        title = re.sub("<.*?>", "", m.group(1)).strip() if m else ""
        titles.append(title)
        vis = visible_text(text)
        bodies.append(vis)
        hashes.append(hashlib.sha1(text.encode()).hexdigest())
        lang_m = re.search(r'lang="([^"]+)"', text)
        lang = lang_m.group(1) if lang_m else "en"
        chars = len(re.sub(r"\s+", "", vis))
        words = len(vis.split())
        if lang in {"ja", "zh-Hant", "zh-Hans", "ko", "th", "ar", "he", "hi"}:
            if chars < 350:
                short.append(d.name)
        elif words < 80:
            short.append(d.name)
        for b in BANNED:
            if b.lower() in text.lower() if b.isascii() else b in text:
                banned_hits.append((d.name, b))
        for b in CHINA_MARKETS:
            if b in text:
                banned_hits.append((d.name, b))
        if "singlinkvpn.com/" not in text or "/download/" not in text:
            bad_cta.append(d.name)
        if "/plan" in text.lower() or "pricing" in text.lower():
            bad_cta.append(d.name)
        for req in ("robots.txt", "sitemap.xml", ".nojekyll"):
            if not (d / req).exists():
                missing.append(f"{d.name}/{req}")
        robots = (d / "robots.txt").read_text(encoding="utf-8") if (d / "robots.txt").exists() else ""
        if "Sitemap:" not in robots:
            missing.append(f"{d.name}/robots-sitemap")
    report = {
        "sites": len(dirs),
        "unique_titles": len(set(titles)),
        "unique_html": len(set(hashes)),
        "short_pages": len(short),
        "banned_hits": banned_hits[:20],
        "missing": missing[:20],
        "bad_cta": bad_cta[:20],
        "ok": (
            len(dirs) == 1000
            and len(set(titles)) == 1000
            and len(set(hashes)) == 1000
            and not short
            and not banned_hits
            and not missing
            and not bad_cta
        ),
    }
    (ROOT / "minisite-verify.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
