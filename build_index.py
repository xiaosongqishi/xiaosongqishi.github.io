"""
Lightweight content index builder — scans posts/*.html for <meta> tags
and generates structured JSON indexes. Zero external dependencies.

Core meta tags:
  <meta name="post-title" content="...">
  <meta name="post-date" content="2026-03-18">
  <meta name="post-summary" content="...">
  <meta name="post-tags" content="LLM, Agents, LangGraph">

Optional structured tags:
  <meta name="post-type" content="post|newsletter">
  <meta name="post-status" content="published|draft">
  <meta name="post-featured" content="true|false">
"""

import json
import re
from datetime import datetime
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

    entries = []

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

        entry_type = extract_meta(html, "post-type").lower() or "post"
        status = extract_meta(html, "post-status").lower() or "published"
        featured = (extract_meta(html, "post-featured").lower() == "true")

        if entry_type not in {"post", "newsletter"}:
            print(f"Unknown post-type in {f.name}: {entry_type!r}. Fallback to 'post'.")
            entry_type = "post"

        entries.append({
            "slug": f.stem,
            "title": title,
            "date": date,
            "summary": summary,
            "tags": tags,
            "url": f"posts/{f.name}",
            "type": entry_type,
            "status": status,
            "featured": featured,
        })

    entries.sort(key=lambda p: p["date"], reverse=True)

    published_entries = [e for e in entries if e["status"] == "published"]
    posts = [e for e in published_entries if e["type"] == "post"]
    newsletters = [e for e in published_entries if e["type"] == "newsletter"]

    content_out = POSTS_DIR / "content-data.json"
    content_out.write_text(
        json.dumps(
            {
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "total": len(entries),
                "published": len(published_entries),
                "posts": len(posts),
                "newsletters": len(newsletters),
                "items": entries,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    posts_out = POSTS_DIR / "posts-data.json"
    posts_out.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")

    newsletters_out = POSTS_DIR / "newsletter-data.json"
    newsletters_out.write_text(json.dumps(newsletters, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        "Built indexes: "
        f"{len(posts)} post(s), {len(newsletters)} newsletter issue(s) "
        f"→ {posts_out.name}, {newsletters_out.name}, {content_out.name}"
    )


if __name__ == "__main__":
    build()
