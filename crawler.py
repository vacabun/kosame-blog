#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@home cafe Maid Blog Crawler
Specially configured for Kosame (Maid ID: 1598)
Crawl all blog entries, profiles, and images.
"""

import os
import sys
import json
import time
import argparse
import urllib.parse
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://www.cafe-athome.com"
API_BLOG_LIST = "https://api.membership.cafe-athome.com/member/v1/get-maid-blog-list"
API_BLOG_DETAIL = "https://api.membership.cafe-athome.com/member/v1/get-maid-blog-detail"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/maid-blog/1598",
}


def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def fetch_blog_list(session, maid_id=1598):
    """
    Fetch all blog list items for the maid.
    Returns (maid_profile, blog_summary_list)
    """
    print(f"[*] Fetching blog list for Maid ID {maid_id}...")
    page = 1
    per_page = 100
    all_blogs = []
    maid_profile = {}

    while True:
        payload = {
            "maidId": maid_id,
            "type": 3,
            "per": per_page,
            "page": page
        }
        resp = session.post(API_BLOG_LIST, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            print(f"[-] API error fetching list page {page}: {data.get('errors')}")
            break

        results = data.get("results", [])
        if not results:
            break

        res_obj = results[0]
        if not maid_profile:
            maid_profile = {k: v for k, v in res_obj.items() if k != "blogs"}

        blogs = res_obj.get("blogs", [])
        if not blogs:
            break

        all_blogs.extend(blogs)
        print(f"    Page {page}: fetched {len(blogs)} posts (total: {len(all_blogs)})")

        if len(blogs) < per_page:
            break

        page += 1
        time.sleep(0.3)

    print(f"[+] Total blog posts discovered: {len(all_blogs)}")
    return maid_profile, all_blogs


def fetch_post_detail(session, maid_id, post_id, retry=3):
    """
    Fetch single post detail by maidId and postId.
    """
    payload = {
        "maidId": maid_id,
        "postId": post_id
    }
    for attempt in range(retry):
        try:
            resp = session.post(API_BLOG_DETAIL, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success") and data.get("results"):
                return data["results"][0]
            else:
                return None
        except Exception as e:
            if attempt == retry - 1:
                print(f"[-] Error fetching post {post_id}: {e}")
                return None
            time.sleep(1)
    return None


def clean_post_html(raw_html):
    """
    Clean up café-athome email blog html wrapper:
    Remove wrapper <html><head></head><body> tags, strip unnecessary inner styles,
    ensure tags are valid and clean for modern responsive display.
    """
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove html, head, body tags if they exist inside the snippet
    for tag in soup(["html", "head", "body", "meta", "title", "style"]):
        tag.unwrap()

    # Clean empty divs or spaces
    cleaned = str(soup)
    return cleaned.strip()


def download_file(session, url, dest_path):
    """
    Download a remote file to local dest_path if not already downloaded.
    """
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return True
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    try:
        r = session.get(url, timeout=25, stream=True)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            return False
    except Exception as e:
        print(f"[-] Failed to download {url}: {e}")
        return False


def run_crawler(maid_id=1598, data_dir="data", download_images=True, force=False, limit=None, delay=0.2):
    """
    Main crawler pipeline:
    1. Fetch list and profile
    2. Download raw post details (with cache)
    3. Process images and clean HTML
    4. Save data/maid.json and data/posts.json
    """
    data_path = Path(data_dir)
    raw_posts_dir = data_path / "raw_posts"
    img_dir = data_path / "images"
    raw_posts_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    session = create_session()

    # 1. Fetch blog list
    maid_profile, blog_summaries = fetch_blog_list(session, maid_id=maid_id)

    # Save maid profile
    maid_file = data_path / "maid.json"
    with open(maid_file, "w", encoding="utf-8") as f:
        json.dump(maid_profile, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved maid profile to {maid_file}")

    # Optionally download maid avatar
    avatar_url = maid_profile.get("maidImg")
    if download_images and avatar_url:
        avatar_name = "avatar_" + os.path.basename(urllib.parse.urlparse(avatar_url).path)
        avatar_path = img_dir / avatar_name
        print(f"[*] Downloading maid avatar: {avatar_url}")
        if download_file(session, avatar_url, avatar_path):
            maid_profile["local_avatar"] = f"images/{avatar_name}"

    # Filter by limit if specified
    if limit and limit > 0:
        blog_summaries = blog_summaries[:limit]

    # Sort summaries by postId ascending (1..302)
    blog_summaries.sort(key=lambda x: int(x["postId"]))

    total_posts = len(blog_summaries)
    print(f"[*] Processing {total_posts} blog posts...")

    detailed_posts = []

    for item in tqdm(blog_summaries, desc="Fetching post details"):
        post_id = int(item["postId"])
        raw_file = raw_posts_dir / f"{post_id}.json"

        post_data = None
        if not force and raw_file.exists():
            try:
                with open(raw_file, "r", encoding="utf-8") as f:
                    post_data = json.load(f)
            except Exception:
                post_data = None

        if not post_data:
            post_data = fetch_post_detail(session, maid_id, post_id)
            if post_data:
                with open(raw_file, "w", encoding="utf-8") as f:
                    json.dump(post_data, f, ensure_ascii=False, indent=2)
            time.sleep(delay)

        if not post_data:
            print(f"[-] Warning: Post {post_id} returned no data, skipping.")
            continue

        detailed_posts.append(post_data)

    # Process posts, download images, rewrite links if needed
    print("[*] Processing post content and localizing images...")
    processed_posts = []

    # Sort detailed posts by postAt or postId ascending
    detailed_posts.sort(key=lambda x: (x.get("postAt") or "", int(x["postId"])))

    for idx, post in enumerate(detailed_posts):
        p_id = post["postId"]
        title = post.get("postTitle") or f"Post #{p_id}"
        date = post.get("postAt") or ""
        body_html = post.get("postText") or ""

        soup = BeautifulSoup(body_html, "html.parser")

        # Unwrap any <html> <head> <body> <meta> <p><HTML> wrappers
        for tag in soup(["html", "head", "body", "meta", "title"]):
            tag.unwrap()

        images_in_post = []
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if not src:
                continue

            full_img_url = urllib.parse.urljoin(BASE_URL, src)
            images_in_post.append(full_img_url)

            if download_images:
                # Determine local file name
                parsed = urllib.parse.urlparse(full_img_url)
                ext = os.path.splitext(parsed.path)[1]
                if not ext:
                    ext = ".jpg"
                clean_name = os.path.basename(parsed.path)
                if not clean_name:
                    clean_name = f"img_{len(images_in_post)}{ext}"
                
                local_rel_dir = f"images/posts/{p_id}"
                local_file_path = data_path / local_rel_dir / clean_name
                local_url = f"../{local_rel_dir}/{clean_name}"

                download_file(session, full_img_url, local_file_path)
                img["src"] = local_url
            else:
                img["src"] = full_img_url

            img["loading"] = "lazy"
            img["class"] = img.get("class", []) + ["post-content-image"]
            # Add alt text if missing
            if not img.get("alt"):
                img["alt"] = f"{title} - image"

        # Also fix any <a href="http://dcimg.awalker.jp/..."> wrapping the images so clicking them doesn't go to broken old site
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href", "")
            if "dcimg.awalker.jp" in href or "/wp-content/" in href:
                # Make it open the image or lightbox
                child_img = a_tag.find("img")
                if child_img:
                    a_tag["href"] = child_img.get("src", href)
                    a_tag["class"] = a_tag.get("class", []) + ["lightbox-trigger"]
                    a_tag["target"] = "_blank"
                    a_tag["rel"] = "noopener noreferrer"

        cleaned_content = str(soup)

        # Excerpt text
        plain_text = soup.get_text(separator=" ").strip()
        # Collapse multiple whitespace
        plain_text = " ".join(plain_text.split())
        excerpt = plain_text[:140] + ("..." if len(plain_text) > 140 else "")

        processed_item = {
            "id": p_id,
            "title": title,
            "date": date,
            "year": date[:4] if len(date) >= 4 else "Unknown",
            "month": date[5:7] if len(date) >= 7 else "01",
            "day": date[8:10] if len(date) >= 10 else "01",
            "time": date[11:16] if len(date) >= 16 else "",
            "excerpt": excerpt,
            "content": cleaned_content,
            "image_count": len(images_in_post),
            "cover_image": images_in_post[0] if images_in_post else None,
            "prev_id": detailed_posts[idx - 1]["postId"] if idx > 0 else None,
            "prev_title": detailed_posts[idx - 1].get("postTitle") if idx > 0 else None,
            "next_id": detailed_posts[idx + 1]["postId"] if idx < len(detailed_posts) - 1 else None,
            "next_title": detailed_posts[idx + 1].get("postTitle") if idx < len(detailed_posts) - 1 else None,
        }
        processed_posts.append(processed_item)

    # Save to data/posts.json (reverse sorted by date for display)
    posts_file = data_path / "posts.json"
    with open(posts_file, "w", encoding="utf-8") as f:
        json.dump(processed_posts, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {len(processed_posts)} processed posts to {posts_file}")

    return maid_profile, processed_posts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Kosame's maid blog posts")
    parser.add_argument("--maid-id", type=int, default=1598, help="Maid ID (default: 1598)")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory to save data")
    parser.add_argument("--no-images", action="store_true", help="Do not download images locally")
    parser.add_argument("--force", action="store_true", help="Force re-fetch all posts")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of posts (for testing)")
    parser.add_argument("--delay", type=float, default=0.15, help="Delay between requests in seconds")

    args = parser.parse_args()

    run_crawler(
        maid_id=args.maid_id,
        data_dir=args.data_dir,
        download_images=not args.no_images,
        force=args.force,
        limit=args.limit,
        delay=args.delay
    )
