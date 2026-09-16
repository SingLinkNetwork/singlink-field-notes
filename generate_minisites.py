#!/usr/bin/env python3
"""Build 1000 standalone mini-sites under minisites/."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from minisite import render_files, write_site

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "minisites"
CATALOG = ROOT / "minisite-catalog.json"


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    catalog = []
    for n in range(1000):
        meta = render_files(n)
        write_site(n, OUT / meta["repo"])
        catalog.append(
            {
                "n": n,
                "repo": meta["repo"],
                "url": meta["url"],
                "title": meta["title"],
                "lang": meta["lang"],
                "city": meta["city"],
                "intent": meta["intent"],
                "slug": meta["slug"],
                "cta": meta["cta"],
            }
        )
        if (n + 1) % 100 == 0:
            print(f"built {n + 1}/1000", flush=True)
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    titles = {row["title"] for row in catalog}
    repos = {row["repo"] for row in catalog}
    print(json.dumps({"sites": len(catalog), "unique_titles": len(titles), "unique_repos": len(repos)}))


if __name__ == "__main__":
    main()
