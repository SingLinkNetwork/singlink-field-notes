#!/usr/bin/env python3
"""Force-push regenerated files to already-created mini-site repos. No new repos."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from minisite import ORG, render_files, write_site
from publish_sites import log, maybe_backoff, run

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "published-sites.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sleep", type=float, default=8)
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    done = 0
    for row in data.get("sites", []):
        if done >= args.limit:
            break
        if row.get("status") not in {"live", "pages_enabled", "pushed"}:
            continue
        meta = render_files(row["n"])
        work = Path(tempfile.mkdtemp(prefix=f"sl-up-{meta['repo']}-"))
        try:
            write_site(row["n"], work)
            run(["git", "init", "-b", "main"], cwd=work)
            run(["git", "add", "-A"], cwd=work)
            run(["git", "commit", "-m", f"Update {meta['city']} field note language/copy"], cwd=work)
            run(
                ["git", "remote", "add", "origin", f"https://github.com/{ORG}/{meta['repo']}.git"],
                cwd=work,
            )
            pushed = run(["git", "push", "-u", "origin", "main", "--force"], cwd=work, timeout=240)
            if pushed.returncode != 0:
                blob = (pushed.stdout or "") + (pushed.stderr or "")
                maybe_backoff(blob)
                log(f"republish fail {meta['repo']}: {blob[-400:]}")
                continue
            done += 1
            log(f"republish {meta['repo']} ({done})")
            time.sleep(args.sleep)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"updated": done}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
