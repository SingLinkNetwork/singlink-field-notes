#!/usr/bin/env python3
"""Create/push/enable GitHub Pages for each mini-site. Resume-safe."""

from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from minisite import ORG, render_files, write_site

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "published-sites.json"
LOG = ROOT / "publish-progress.log"
LOCK = threading.Lock()
DONE = 0
DONE_LOCK = threading.Lock()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"{now()} {msg}"
    print(line, flush=True)
    with LOCK:
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"target": 1000, "updated": None, "sites": []}


def save_manifest(data: dict) -> None:
    data["updated"] = now()
    tmp = MANIFEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(MANIFEST)


def site_entry(data: dict, n: int) -> dict | None:
    for row in data["sites"]:
        if row["n"] == n:
            return row
    return None


def upsert(row: dict) -> None:
    with LOCK:
        data = load_manifest()
        for i, existing in enumerate(data["sites"]):
            if existing["n"] == row["n"]:
                data["sites"][i] = row
                save_manifest(data)
                return
        data["sites"].append(row)
        data["sites"].sort(key=lambda r: r["n"])
        save_manifest(data)


def current_row(n: int) -> dict | None:
    with LOCK:
        return site_entry(load_manifest(), n)


def run(cmd: list[str], cwd=None, timeout=180) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)


def repo_exists(repo: str) -> bool:
    r = run(["gh", "repo", "view", f"{ORG}/{repo}", "--json", "name"])
    return r.returncode == 0


def enable_pages(repo: str) -> tuple[bool, str]:
    r = run(
        [
            "gh",
            "api",
            "--method",
            "POST",
            f"repos/{ORG}/{repo}/pages",
            "-H",
            "Accept: application/vnd.github+json",
            "-f",
            "build_type=legacy",
            "-f",
            "source[branch]=main",
            "-f",
            "source[path]=/",
        ]
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0 or "already exists" in out.lower() or "already enabled" in out.lower():
        return True, out[-400:]
    r2 = run(["gh", "api", f"repos/{ORG}/{repo}/pages"])
    if r2.returncode == 0:
        return True, (r2.stdout or "")[-400:]
    return False, out[-800:]


def http_status(url: str) -> int:
    r = run(
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
        timeout=30,
    )
    try:
        return int((r.stdout or "").strip() or "0")
    except ValueError:
        return 0


def maybe_backoff(text: str) -> bool:
    low = text.lower()
    if "too many repositories" in low or "too quickly" in low:
        log("repo-create throttle; sleeping 900s")
        time.sleep(900)
        return True
    if "secondary rate limit" in low or "abuse detection" in low:
        log("secondary rate limit; sleeping 90s")
        time.sleep(90)
        return True
    if "rate limit" in low:
        log("rate limit; sleeping 60s")
        time.sleep(60)
        return True
    return False


def publish_one(n: int, sleep_s: float, wait_http: bool) -> dict:
    meta = render_files(n)
    row = current_row(n) or {
        "n": n,
        "repo": meta["repo"],
        "url": meta["url"],
        "title": meta["title"],
        "status": "pending",
        "http_status": None,
        "error": None,
        "created_at": now(),
    }
    if row.get("status") == "live" and row.get("http_status") == 200:
        return row
    if row.get("status") in {"pages_enabled", "pushed"} and not wait_http:
        # Already created this session or a prior one; only refresh HTTP if asked.
        status = http_status(meta["url"])
        row["http_status"] = status
        if status == 200:
            row["status"] = "live"
            row["error"] = None
        upsert(row)
        return row

    work = Path(tempfile.mkdtemp(prefix=f"sl-{meta['repo']}-"))
    try:
        write_site(n, work)
        git = run(["git", "init", "-b", "main"], cwd=work)
        if git.returncode != 0:
            raise RuntimeError(git.stderr)
        run(["git", "add", "-A"], cwd=work)
        msg = f"Publish {meta['city']} field note ({meta['title'][:80]})"
        cm = run(["git", "commit", "-m", msg], cwd=work)
        if cm.returncode != 0 and "nothing to commit" not in (cm.stdout + cm.stderr):
            raise RuntimeError(cm.stderr)

        exists = repo_exists(meta["repo"])
        if not exists:
            for attempt in range(6):
                created = run(
                    [
                        "gh",
                        "repo",
                        "create",
                        f"{ORG}/{meta['repo']}",
                        "--public",
                        "--description",
                        meta["description"],
                        "--homepage",
                        meta["url"],
                        "--disable-issues",
                        "--disable-wiki",
                        "--source",
                        ".",
                        "--remote",
                        "origin",
                        "--push",
                    ],
                    cwd=work,
                    timeout=240,
                )
                blob = (created.stdout or "") + (created.stderr or "")
                if created.returncode == 0:
                    row["status"] = "pushed"
                    row["error"] = None
                    upsert(row)
                    break
                if "already exists" in blob.lower():
                    exists = True
                    break
                if maybe_backoff(blob) and attempt < 5:
                    log(f"retry create {meta['repo']} attempt {attempt + 2}")
                    continue
                raise RuntimeError(blob[-800:])
        if exists:
            run(["git", "remote", "remove", "origin"], cwd=work)
            run(
                ["git", "remote", "add", "origin", f"https://github.com/{ORG}/{meta['repo']}.git"],
                cwd=work,
            )
            pushed = run(["git", "push", "-u", "origin", "main", "--force"], cwd=work, timeout=240)
            if pushed.returncode != 0:
                blob = (pushed.stdout or "") + (pushed.stderr or "")
                maybe_backoff(blob)
                raise RuntimeError(blob[-800:])
            row["status"] = "pushed"
            row["error"] = None
            upsert(row)

        ok, detail = enable_pages(meta["repo"])
        if not ok:
            maybe_backoff(detail)
            row["status"] = "pushed"
            row["error"] = f"pages: {detail}"
        else:
            row["status"] = "pages_enabled"
            row["error"] = None
        upsert(row)

        if wait_http:
            time.sleep(6)
            status = http_status(meta["url"])
            if status != 200:
                time.sleep(12)
                status = http_status(meta["url"])
            row["http_status"] = status
            if status == 200:
                row["status"] = "live"
                row["error"] = None
            upsert(row)
        log(f"n={n+1:04d} {meta['repo']} status={row['status']} http={row.get('http_status')}")
        time.sleep(sleep_s + random.uniform(0, 0.4))
        return row
    except Exception as exc:
        row["status"] = "failed"
        row["error"] = str(exc)[-800:]
        upsert(row)
        log(f"n={n+1:04d} FAILED {meta['repo']}: {row['error']}")
        time.sleep(max(sleep_s, 2))
        return row
    finally:
        shutil.rmtree(work, ignore_errors=True)


def counts(data: dict | None = None) -> dict:
    if data is None:
        with LOCK:
            data = load_manifest()
    out = {"live": 0, "pages_enabled": 0, "pushed": 0, "failed": 0, "other": 0, "total": len(data["sites"])}
    for row in data["sites"]:
        st = row.get("status")
        if row.get("http_status") == 200:
            out["live"] += 1
        elif st in out:
            out[st] += 1
        else:
            out["other"] += 1
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--sleep", type=float, default=0.8)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--wait-http", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()

    end = min(1000, args.start + args.limit)
    todo = []
    with LOCK:
        data = load_manifest()
    for n in range(args.start, end):
        row = site_entry(data, n)
        if row and row.get("status") == "live" and row.get("http_status") == 200:
            continue
        if row and row.get("status") == "failed" and not args.retry_failed:
            err = (row.get("error") or "").lower()
            if "not allowed" in err or "cannot be created" in err:
                continue
        todo.append(n)
    log(f"publish start={args.start} end={end} todo={len(todo)} already={counts(data)} conc={args.concurrency}")

    def worker(n: int) -> dict:
        global DONE
        row = publish_one(n, args.sleep, args.wait_http)
        with DONE_LOCK:
            DONE += 1
            d = DONE
        if d % 10 == 0:
            log(f"progress {counts()}")
        return row

    if args.concurrency <= 1:
        for n in todo:
            worker(n)
    else:
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futs = [pool.submit(worker, n) for n in todo]
            for fut in as_completed(futs):
                fut.result()
    log(f"publish loop done {counts()}")
    print(json.dumps(counts()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
