"""
Downloading a Roblox user's 3D avatar by User ID.

Usage:
pip install requests
python roblox_avatar_download.py

By default it downloads the avatar for the USER_ID set below.
"""

import json
import re
import time
from pathlib import Path

import requests

USER_ID = "11178926669"
OUT_DIR = Path(f"avatar_{USER_ID}")
OUT_DIR.mkdir(parents=True, exist_ok=True)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def safe_name(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9._-]+', '_', s)


def get_json(url: str) -> dict:
    r = requests.get(url, headers=HEADERS, timeout=30)
    if not r.ok:
        raise RuntimeError(
            f"HTTP {r.status_code} on request {url}\nServer response: {r.text[:500]}"
        )
    return r.json()


def download_any_cdn(hash_value: str) -> bytes:
    """Roblox serves static files through t0..t7.rbxcdn.com — we try the nodes in turn."""
    last_err = None
    for n in range(8):
        url = f"https://t{n}.rbxcdn.com/{hash_value}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
        except requests.RequestException as e:
            last_err = str(e)
            continue
        if r.status_code == 200 and r.content:
            return r.content
        last_err = f"{r.status_code} {url}"
    raise RuntimeError(last_err or f"Could not download {hash_value}")


def fetch_avatar_bundle(user_id: str, max_wait_seconds: int = 30) -> dict:
    """Requests a 3D avatar preview, waiting until it is ready (state=Completed)."""
    api_url = f"https://thumbnails.roblox.com/v1/users/avatar-3d?userId={user_id}"
    waited = 0
    while True:
        resp = get_json(api_url)
        item = resp["data"][0]
        state = item.get("state")
        if state == "Completed":
            bundle = get_json(item["imageUrl"])
            bundle["_api_url"] = api_url
            bundle["_preview_url"] = item["imageUrl"]
            return bundle
        if state == "Error" or waited >= max_wait_seconds:
            raise RuntimeError(f"The avatar is not ready (state={state}): {item}")
        time.sleep(2)
        waited += 2


def main():
    print(f"Requesting the 3D avatar for userId={USER_ID}...")
    bundle = fetch_avatar_bundle(USER_ID)

    obj_hash = bundle["obj"]
    mtl_hash = bundle["mtl"]
    textures = bundle.get("textures", [])

    obj_bytes = download_any_cdn(obj_hash)
    mtl_bytes = download_any_cdn(mtl_hash)

    obj_path = OUT_DIR / f"{safe_name(obj_hash)}.obj"
    mtl_path = OUT_DIR / f"{safe_name(mtl_hash)}.mtl"
    obj_path.write_bytes(obj_bytes)
    mtl_path.write_bytes(mtl_bytes)

    tex_files = []
    for tex in textures:
        tex_bytes = download_any_cdn(tex)
        tex_path = OUT_DIR / f"{safe_name(tex)}.png"
        tex_path.write_bytes(tex_bytes)
        tex_files.append(tex_path.name)

    meta = {
        "userId": USER_ID,
        "api_url": bundle["_api_url"],
        "preview_url": bundle["_preview_url"],
        "obj": str(obj_path),
        "mtl": str(mtl_path),
        "textures": tex_files,
        "camera": bundle.get("camera"),
        "aabb": bundle.get("aabb"),
    }
    (OUT_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("Done:", OUT_DIR.resolve())


if __name__ == "__main__":
    main()
