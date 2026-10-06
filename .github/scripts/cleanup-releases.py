#!/usr/bin/env python3
"""Удаляет старые GitHub-релизы (и их теги), оставляя самые свежие.

Правила (что остаётся):
  1. минимум KEEP релизов (по умолчанию 5, меньше 5 задать нельзя) —
     самые новые по дате создания;
  2. минимум один stable-релиз (не prerelease, не draft). В CI stable —
     это полный релиз с APK (тег v1.N), а hot-update релизы (тег hot-N)
     помечены prerelease. Если среди свежих KEEP релизов stable нет
     (например, подряд вышли одни hot-update), дополнительно сохраняется
     самый новый stable из более старых — чтобы releases/latest и ссылка
     на app-debug.apk не сломались.

Draft-релизы не трогаем вообще.

По умолчанию — dry-run (только показывает, что будет удалено).
Реальное удаление — с флагом --apply.

Использование:
  export GITHUB_TOKEN=ghp_...        # нужен scope repo (для --apply)
  python3 .github/scripts/cleanup-releases.py                  # dry-run
  python3 .github/scripts/cleanup-releases.py --apply          # удалить
  python3 .github/scripts/cleanup-releases.py --keep 8 --apply
  python3 .github/scripts/cleanup-releases.py --apply --keep-tags

Только стандартная библиотека Python 3, зависимостей нет.
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
    """owner/name из git remote origin; если не вышло — репозиторий по умолчанию."""
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
    """Возвращает (оставить, удалить). releases — любые, draft игнорируются."""
    published = [r for r in releases if not r["draft"]]
    published.sort(key=lambda r: r["created_at"], reverse=True)

    kept = published[:keep]
    rest = published[keep:]

    # Гарантируем хотя бы один stable среди оставленных.
    if not any(is_stable(r) for r in kept):
        extra = next((r for r in rest if is_stable(r)), None)
        if extra:
            kept.append(extra)
            rest.remove(extra)
        else:
            print("ВНИМАНИЕ: в репозитории вообще нет stable-релизов "
                  "(все prerelease) — условие 'минимум один stable' выполнить нечем.",
                  file=sys.stderr)
    return kept, rest


def label(rel):
    kind = "stable" if is_stable(rel) else "prerelease"
    return f"{rel['tag_name']:<12} {kind:<10} {rel['created_at'][:10]}  {rel['name'] or ''}"


def main():
    ap = argparse.ArgumentParser(description="Удаление старых GitHub-релизов")
    ap.add_argument("--repo", default=None, help="owner/name (по умолчанию из git remote)")
    ap.add_argument("--keep", type=int, default=MIN_KEEP,
                    help=f"сколько свежих релизов оставить (минимум {MIN_KEEP})")
    ap.add_argument("--apply", action="store_true",
                    help="реально удалять (без флага — только dry-run)")
    ap.add_argument("--keep-tags", action="store_true",
                    help="не удалять git-теги удалённых релизов")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="пауза между удалениями, сек (защита от secondary rate limit)")
    args = ap.parse_args()

    if args.keep < MIN_KEEP:
        ap.error(f"--keep не может быть меньше {MIN_KEEP}")

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if args.apply and not token:
        sys.exit("Для --apply нужен токен: export GITHUB_TOKEN=...")

    repo = args.repo or detect_repo()
    print(f"Репозиторий: {repo}")

    try:
        releases = list_releases(repo, token)
    except urllib.error.HTTPError as e:
        sys.exit(f"Не удалось получить релизы: HTTP {e.code} {e.reason}")

    kept, to_delete = plan(releases, args.keep)
    print(f"Всего релизов (без draft): {len(kept) + len(to_delete)}")

    print(f"\nОставляем ({len(kept)}):")
    for r in kept:
        print("  +", label(r))

    if not to_delete:
        print("\nУдалять нечего.")
        return

    print(f"\nУдаляем ({len(to_delete)}):")
    for r in to_delete:
        print("  -", label(r))

    if not args.apply:
        print("\nЭто dry-run. Для удаления запусти с --apply.")
        return

    print()
    failed = 0
    for r in to_delete:
        try:
            request("DELETE", f"/repos/{repo}/releases/{r['id']}", token)
            msg = f"удалён релиз {r['tag_name']}"
            if not args.keep_tags and r.get("tag_name"):
                try:
                    request("DELETE", f"/repos/{repo}/git/refs/tags/{r['tag_name']}", token)
                    msg += " + тег"
                except urllib.error.HTTPError as e:
                    # 404/422 — тега уже нет, это нормально
                    if e.code not in (404, 422):
                        raise
            print("  ✓", msg)
        except urllib.error.HTTPError as e:
            failed += 1
            print(f"  ✗ {r['tag_name']}: HTTP {e.code} {e.reason}", file=sys.stderr)
        time.sleep(args.delay)

    if failed:
        sys.exit(f"Готово, но {failed} не удалось удалить.")
    print("\nГотово.")


if __name__ == "__main__":
    main()
