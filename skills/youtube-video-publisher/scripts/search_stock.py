#!/usr/bin/env python3
"""Search Pexels and Pixabay videos without printing API keys."""

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


def load_env(path):
    if not path:
        return
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_json(url, headers=None):
    request_headers = {"User-Agent": "Codex-Stock-Video-Skill/1.0", "Accept": "application/json"}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def pexels(query, orientation, per_page):
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return [], "PEXELS_API_KEY is missing"
    params = urllib.parse.urlencode({"query": query, "orientation": orientation, "per_page": per_page})
    data = get_json("https://api.pexels.com/videos/search?" + params, {"Authorization": key})
    results = []
    for video in data.get("videos", []):
        files = sorted(video.get("video_files", []), key=lambda f: (f.get("width") or 0) * (f.get("height") or 0), reverse=True)
        if not files:
            continue
        item = files[0]
        results.append({"provider": "pexels", "id": video.get("id"), "duration": video.get("duration"), "width": item.get("width"), "height": item.get("height"), "source_page_url": video.get("url"), "download_url": item.get("link"), "creator": (video.get("user") or {}).get("name"), "query": query})
    return results, None


def pixabay(query, orientation, per_page):
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        return [], "PIXABAY_API_KEY is missing"
    params = urllib.parse.urlencode({"key": key, "q": query, "per_page": per_page, "safesearch": "true"})
    data = get_json("https://pixabay.com/api/videos/?" + params)
    results = []
    for video in data.get("hits", []):
        candidates = [v for v in (video.get("videos") or {}).values() if isinstance(v, dict) and v.get("url")]
        candidates.sort(key=lambda f: (f.get("width") or 0) * (f.get("height") or 0), reverse=True)
        for item in candidates:
            width, height = item.get("width") or 0, item.get("height") or 0
            if orientation == "landscape" and width < height:
                continue
            if orientation == "portrait" and height < width:
                continue
            results.append({"provider": "pixabay", "id": video.get("id"), "duration": video.get("duration"), "width": width, "height": height, "source_page_url": video.get("pageURL"), "download_url": item.get("url"), "creator": video.get("user"), "query": query})
            break
    return results, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--env-file")
    parser.add_argument("--orientation", choices=["landscape", "portrait"], default="landscape")
    parser.add_argument("--per-page", type=int, default=12)
    args = parser.parse_args()
    load_env(args.env_file)
    output, warnings = [], []
    for search in (pexels, pixabay):
        try:
            items, warning = search(args.query, args.orientation, args.per_page)
            output.extend(items)
            if warning:
                warnings.append(warning)
        except Exception as exc:
            warnings.append(f"{search.__name__}: {type(exc).__name__}: {exc}")
    print(json.dumps({"results": output, "warnings": warnings}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
