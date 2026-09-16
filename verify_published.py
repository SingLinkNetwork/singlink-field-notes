#!/usr/bin/env python3
"""HTTP-verify published mini-sites from published-sites.json."""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "published-sites.json"
REPORT = ROOT / "publish-report.json"


def curl_code(url: str) -> int:
    r = subprocess.run(
        [
            "/usr/bin/curl",
            "-sI",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            "-A",
            "Mozilla/5.0 SingLinkFieldNotesVerify/1.0",
            "--max-time",
            "20",
            url,
        ],
        text=True,
        capture_output=True,
        timeout=30,
    )
    try:
        return int((r.stdout or "").strip() or "0")
    except ValueError:
        return 0


def sitemap_ok(url: str) -> bool:
    sitemap = url.rstrip("/") + "/sitemap.xml"
    return curl_code(sitemap) == 200


def robots_ok(url: str) -> bool:
    robots = url.rstrip("/") + "/robots.txt"
    return curl_code(robots) == 200


def main() -> int:
    if not MANIFEST.exists():
        print("missing published-sites.json", file=sys.stderr)
        return 1
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sites = data.get("sites", [])
    results = []

    def check(row):
        url = row["url"]
        code = curl_code(url)
        return {
            "n": row["n"],
            "repo": row["repo"],
            "url": url,
            "title": row.get("title"),
            "http_status": code,
            "sitemap": sitemap_ok(url) if code == 200 else False,
            "robots": robots_ok(url) if code == 200 else False,
        }

    with ThreadPoolExecutor(max_workers=12) as pool:
        futs = [pool.submit(check, row) for row in sites]
        for fut in as_completed(futs):
            results.append(fut.result())
    results.sort(key=lambda r: r["n"])
    live = [r for r in results if r["http_status"] == 200]
    with_maps = [r for r in live if r["sitemap"] and r["robots"]]
    titles = [r["title"] for r in live if r.get("title")]
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "manifest_sites": len(sites),
        "checked": len(results),
        "http_200": len(live),
        "http_200_with_sitemap_robots": len(with_maps),
        "unique_live_titles": len(set(titles)),
        "first5": [r["url"] for r in live[:5]],
        "last5": [r["url"] for r in live[-5:]],
        "non_200": [
            {"url": r["url"], "http_status": r["http_status"]}
            for r in results
            if r["http_status"] != 200
        ][:50],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # refresh http_status on manifest
    by_n = {r["n"]: r for r in results}
    for row in sites:
        got = by_n.get(row["n"])
        if not got:
            continue
        row["http_status"] = got["http_status"]
        if got["http_status"] == 200:
            row["status"] = "live"
    data["sites"] = sites
    data["updated"] = report["checked_at"]
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "non_200"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
