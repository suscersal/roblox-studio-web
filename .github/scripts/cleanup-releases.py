#!/usr/bin/env python3
"""Deletes old GitHub releases (and their tags), keeping the newest ones.

Rules (what stays):
  1. at least KEEP releases (5 by default, it can't be set below 5) —
     the newest by creation date;
  2. at least one stable release (not a prerelease, not a draft). In CI a stable one is
     a full release with an APK (tag v1.N), while hot-update releases (tag hot-N)
     are marked prerelease. If there is no stable one among the newest KEEP releases
     (for example, only hot-updates came out in a row), the newest stable one among the older ones is additionally kept —
     so that releases/latest and the link
     to app-debug.apk don't break.

Draft releases are not touched at all.

By default — a dry run (it only shows what would be deleted).
Real deletion — with the --apply flag.

Usage:
  export GITHUB_TOKEN=ghp_...        # the repo scope is needed (for --apply)
  python3 .github/scripts/cleanup-releases.py                  # dry run
  python3 .github/scripts/cleanup-releases.py --apply          # delete
  python3 .github/scripts/cleanup-releases.py --keep 8 --apply
  python3 .github/scripts/cleanup-releases.py --apply --keep-tags

Python 3 standard library only, no dependencies.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"
MIN_KEEP = 5
DEFAULT_REPO = "suscersal/roblox-studio-web"


def detect_repo():
    """owner/name from git remote origin; if that fails — the default repository."""
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
        m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
        if m:
            return m.group(1)
    except Exception:
        pass
    return DEFAULT_REPO


def request(method, path, token):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "cleanup-releases-script")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req) as resp:
        body = resp.read()
        return json.loads(body) if body else None


def list_releases(repo, token):
    releases, page = [], 1
    while True:
        chunk = request("GET", f"/repos/{repo}/releases?per_page=100&page={page}", token)
        if not chunk:
            break
        releases.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return releases


def is_stable(rel):
    return not rel["prerelease"] and not rel["draft"]


def plan(releases, keep):
    """Returns (keep, delete). releases — any, drafts are ignored."""
    published = [r for r in releases if not r["draft"]]
    published.sort(key=lambda r: r["created_at"], reverse=True)

    kept = published[:keep]
    rest = published[keep:]

    # We guarantee at least one stable among the kept ones.
    if not any(is_stable(r) for r in kept):
        extra = next((r for r in rest if is_stable(r)), None)
        if extra:
            kept.append(extra)
            rest.remove(extra)
        else:
            print("WARNING: the repository has no stable releases at all "
                  "(all are prereleases) — there is nothing to satisfy the 'at least one stable' condition with.",
                  file=sys.stderr)
    return kept, rest


def label(rel):
    kind = "stable" if is_stable(rel) else "prerelease"
    return f"{rel['tag_name']:<12} {kind:<10} {rel['created_at'][:10]}  {rel['name'] or ''}"


def main():
    ap = argparse.ArgumentParser(description="Deleting old GitHub releases")
    ap.add_argument("--repo", default=None, help="owner/name (from git remote by default)")
    ap.add_argument("--keep", type=int, default=MIN_KEEP,
                    help=f"how many fresh releases to keep (minimum {MIN_KEEP})")
    ap.add_argument("--apply", action="store_true",
                    help="really delete (without the flag — dry run only)")
    ap.add_argument("--keep-tags", action="store_true",
                    help="don't delete the git tags of deleted releases")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="pause between deletions, sec (protection from the secondary rate limit)")
    args = ap.parse_args()

    if args.keep < MIN_KEEP:
        ap.error(f"--keep cannot be less than {MIN_KEEP}")

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if args.apply and not token:
        sys.exit("--apply needs a token: export GITHUB_TOKEN=...")

    repo = args.repo or detect_repo()
    print(f"Repository: {repo}")

    try:
        releases = list_releases(repo, token)
    except urllib.error.HTTPError as e:
        sys.exit(f"Could not get releases: HTTP {e.code} {e.reason}")

    kept, to_delete = plan(releases, args.keep)
    print(f"Total releases (without drafts): {len(kept) + len(to_delete)}")

    print(f"\nKeeping ({len(kept)}):")
    for r in kept:
        print("  +", label(r))

    if not to_delete:
        print("\nNothing to delete.")
        return

    print(f"\nDeleting ({len(to_delete)}):")
    for r in to_delete:
        print("  -", label(r))

    if not args.apply:
        print("\nThis is a dry run. To delete, run with --apply.")
        return

    print()
    failed = 0
    for r in to_delete:
        try:
            request("DELETE", f"/repos/{repo}/releases/{r['id']}", token)
            msg = f"release deleted {r['tag_name']}"
            if not args.keep_tags and r.get("tag_name"):
                try:
                    request("DELETE", f"/repos/{repo}/git/refs/tags/{r['tag_name']}", token)
                    msg += " + tag"
                except urllib.error.HTTPError as e:
                    # 404/422 — the tag is already gone, that's fine
                    if e.code not in (404, 422):
                        raise
            print("  ✓", msg)
        except urllib.error.HTTPError as e:
            failed += 1
            print(f"  ✗ {r['tag_name']}: HTTP {e.code} {e.reason}", file=sys.stderr)
        time.sleep(args.delay)

    if failed:
        sys.exit(f"Done, but {failed} could not be deleted.")
    print("\nDone.")


if __name__ == "__main__":
    main()
