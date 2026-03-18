"""
Lightweight index builder — scans posts/*.html for <meta> tags,
generates posts/posts-data.json. Zero external dependencies.

Expected meta tags in each post HTML:
  <meta name="post-title" content="...">
  <meta name="post-date" content="2026-03-18">
  <meta name="post-summary" content="...">
  <meta name="post-tags" content="LLM, Agents, LangGraph">
"""

import json
import re
from pathlib import Path

POSTS_DIR = Path("posts")


def extract_meta(html: str, name: str) -> str:
    match = re.search(
        rf'<meta\s+name="{name}"\s+content="([^"]*)"', html, re.IGNORECASE
    )
    return match.group(1).strip() if match else ""


def build():
    if not POSTS_DIR.exists():
        print("No posts/ directory found.")
        return

    posts = []

    for f in sorted(POSTS_DIR.glob("*.html")):
        html = f.read_text(encoding="utf-8")
        title = extract_meta(html, "post-title")
        date = extract_meta(html, "post-date")
        summary = extract_meta(html, "post-summary")
        tags_str = extract_meta(html, "post-tags")
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

        if not title:
            print(f"Skipping {f.name}: no post-title meta tag")
            continue

        posts.append({
            "slug": f.stem,
            "title": title,
            "date": date,
            "summary": summary,
            "tags": tags,
            "url": f"posts/{f.name}",
        })

    posts.sort(key=lambda p: p["date"], reverse=True)

    out = POSTS_DIR / "posts-data.json"
    out.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Built index: {len(posts)} post(s) → {out}")


if __name__ == "__main__":
    build()
