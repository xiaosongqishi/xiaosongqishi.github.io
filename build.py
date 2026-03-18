"""
Build script: scans posts/ directory, converts Markdown to HTML,
generates individual post pages and a posts-data.json manifest.
"""

import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

import yaml
import markdown

POSTS_SRC = Path("posts")
DIST_DIR = Path("dist/posts")
TEMPLATE_PATH = Path("post-template.html")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a Markdown file."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return meta, body


def build():
    if not POSTS_SRC.exists():
        print("No posts/ directory found. Nothing to build.")
        return

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    md = markdown.Markdown(
        extensions=["fenced_code", "codehilite", "tables", "toc"],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": False}
        },
    )

    posts_data = []

    for post_dir in sorted(POSTS_SRC.iterdir()):
        if not post_dir.is_dir():
            continue

        md_file = post_dir / "index.md"
        if not md_file.exists():
            print(f"Skipping {post_dir.name}: no index.md found")
            continue

        raw = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)

        title = meta.get("title", post_dir.name)
        post_date = meta.get("date", "")
        summary = meta.get("summary", "")
        tags = meta.get("tags", [])

        if isinstance(post_date, date):
            post_date = post_date.isoformat()

        md.reset()
        html_content = md.convert(body)

        tags_html = "".join(f'<span class="post-tag">{t}</span>' for t in tags)

        page_html = (
            template
            .replace("{{TITLE}}", title)
            .replace("{{DATE}}", str(post_date))
            .replace("{{TAGS}}", tags_html)
            .replace("{{CONTENT}}", html_content)
        )

        out_dir = DIST_DIR / post_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(page_html, encoding="utf-8")

        # Copy assets (images, etc.)
        for asset in post_dir.iterdir():
            if asset.name == "index.md":
                continue
            dest = out_dir / asset.name
            if asset.is_file():
                shutil.copy2(asset, dest)
            elif asset.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(asset, dest)

        posts_data.append({
            "slug": post_dir.name,
            "title": title,
            "date": str(post_date),
            "summary": summary,
            "tags": tags,
            "url": f"dist/posts/{post_dir.name}/index.html",
        })

    posts_data.sort(key=lambda p: p["date"], reverse=True)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "posts-data.json").write_text(
        json.dumps(posts_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Built {len(posts_data)} post(s) → {DIST_DIR}/")


if __name__ == "__main__":
    build()
