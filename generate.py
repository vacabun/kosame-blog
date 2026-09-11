#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static Site Generator for Kosame Maid Blog
Compiles scraped JSON data into a standalone static site in docs/ (GitHub Pages ready).
"""

import os
import sys
import json
import shutil
import html
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


def nl2br_filter(value):
    if not value:
        return ""
    return value.replace("\r\n", "<br>").replace("\n", "<br>")


def setup_jinja_env(templates_dir="templates"):
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"])
    )
    env.filters["nl2br"] = nl2br_filter
    return env


def compute_site_stats(posts):
    total_images = sum(p.get("image_count", 0) for p in posts)
    year_counts = {}

    for p in posts:
        y = p.get("year", "Unknown")
        year_counts[y] = year_counts.get(y, 0) + 1

    # Sorted year counts descending
    sorted_years = dict(sorted(year_counts.items(), key=lambda x: x[0], reverse=True))

    dates = [p.get("date") for p in posts if p.get("date")]
    if dates:
        dates_sorted = sorted(dates)
        start_date = dates_sorted[0][:7].replace("-", ".")
        end_date = dates_sorted[-1][:7].replace("-", ".")
        date_range = f"{start_date} ~ {end_date}"
    else:
        date_range = "2022.11 ~ 2024.07"

    return {
        "total_posts": len(posts),
        "total_images": total_images,
        "year_counts": sorted_years,
        "date_range": date_range
    }


def build_timeline(posts):
    """
    Build hierarchical timeline structure:
    {
       "2024": {
           "total": 134,
           "months": {
               "07": [post, post, ...],
               "06": [...]
           }
       },
       ...
    }
    """
    # Sort posts reverse chronologically for timeline display
    sorted_posts = sorted(posts, key=lambda x: (x.get("date") or "", int(x["id"])), reverse=True)

    timeline = {}
    for p in sorted_posts:
        year = p.get("year", "Unknown")
        month = p.get("month", "01")

        if year not in timeline:
            timeline[year] = {"total": 0, "months": {}}

        timeline[year]["total"] += 1
        if month not in timeline[year]["months"]:
            timeline[year]["months"][month] = []

        timeline[year]["months"][month].append(p)

    return timeline


def generate_site(data_dir="data", output_dir="docs", templates_dir="templates", static_dir="static"):
    data_path = Path(data_dir)
    out_path = Path(output_dir)
    posts_out = out_path / "posts"

    out_path.mkdir(parents=True, exist_ok=True)
    posts_out.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    maid_file = data_path / "maid.json"
    posts_file = data_path / "posts.json"

    if not maid_file.exists() or not posts_file.exists():
        print(f"[-] Error: Data files missing in {data_dir}. Run crawler.py first.")
        sys.exit(1)

    with open(maid_file, "r", encoding="utf-8") as f:
        maid = json.load(f)

    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    # Unescape titles in memory
    for p in posts:
        if "title" in p and p["title"]:
            p["title"] = html.unescape(p["title"])

    print(f"[*] Loaded maid profile ({maid.get('maidName')}) and {len(posts)} posts.")

    # Calculate statistics & timeline
    stats = compute_site_stats(posts)
    timeline = build_timeline(posts)

    # Posts in reverse order (newest first) for homepage list
    posts_newest_first = sorted(posts, key=lambda x: (x.get("date") or "", int(x["id"])), reverse=True)

    # Map for easy lookup by ID
    post_map = {int(p["id"]): p for p in posts}

    # Setup Jinja2
    env = setup_jinja_env(templates_dir)

    # 2. Render Index Page
    print("[*] Generating index.html...")
    index_tpl = env.get_template("index.html")
    index_html = index_tpl.render(
        maid=maid,
        posts=posts_newest_first,
        stats=stats,
        root_path="./",
        active_page="home"
    )
    with open(out_path / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # 3. Render Archive Page
    print("[*] Generating archive.html...")
    archive_tpl = env.get_template("archive.html")
    archive_html = archive_tpl.render(
        maid=maid,
        posts=posts_newest_first,
        timeline=timeline,
        stats=stats,
        root_path="./",
        active_page="archive"
    )
    with open(out_path / "archive.html", "w", encoding="utf-8") as f:
        f.write(archive_html)

    # 4. Render About Page
    print("[*] Generating about.html...")
    about_tpl = env.get_template("about.html")
    about_html = about_tpl.render(
        maid=maid,
        stats=stats,
        root_path="./",
        active_page="about"
    )
    with open(out_path / "about.html", "w", encoding="utf-8") as f:
        f.write(about_html)

    # 5. Render Post Detail Pages
    print(f"[*] Generating {len(posts)} post pages in posts/...")
    post_tpl = env.get_template("post.html")

    for p in posts:
        p_id = int(p["id"])
        prev_post = post_map.get(int(p["prev_id"])) if p.get("prev_id") else None
        next_post = post_map.get(int(p["next_id"])) if p.get("next_id") else None

        post_html = post_tpl.render(
            maid=maid,
            post=p,
            prev_post=prev_post,
            next_post=next_post,
            root_path="../",
            active_page="posts"
        )
        with open(posts_out / f"{p_id}.html", "w", encoding="utf-8") as f:
            f.write(post_html)

    # 6. Copy Static Assets
    print("[*] Copying static assets (CSS, JS, Fonts)...")
    out_static = out_path / "static"
    if out_static.exists():
        shutil.rmtree(out_static)
    shutil.copytree(static_dir, out_static)

    # 7. Copy downloaded images if present
    data_images = data_path / "images"
    out_images = out_path / "images"
    if data_images.exists():
        print("[*] Copying local images to docs/images/...")
        if out_images.exists():
            shutil.rmtree(out_images)
        shutil.copytree(data_images, out_images)

    # 8. Add .nojekyll for GitHub Pages compatibility
    nojekyll_file = out_path / ".nojekyll"
    nojekyll_file.touch()

    print(f"[+] Static site generated successfully at: {out_path.resolve()}/")
    print(f"    - Index: {out_path / 'index.html'}")
    print(f"    - Archive: {out_path / 'archive.html'}")
    print(f"    - Posts: {len(posts)} files in {posts_out}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate static site for Kosame Blog")
    parser.add_argument("--data-dir", type=str, default="data", help="Path to scraped data directory")
    parser.add_argument("--output-dir", type=str, default="docs", help="Output directory (default: docs)")
    parser.add_argument("--templates-dir", type=str, default="templates", help="Templates directory")
    parser.add_argument("--static-dir", type=str, default="static", help="Static directory")

    args = parser.parse_args()
    generate_site(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        templates_dir=args.templates_dir,
        static_dir=args.static_dir
    )
