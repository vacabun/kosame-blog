#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-click Build Script for Kosame Maid Blog Archive
Supports: Crawling, Local Image Downloading, Static Site Building, and Local Preview.
"""

import sys
import argparse
import subprocess
from pathlib import Path
from crawler import run_crawler
from generate import generate_site


def serve_preview(directory="docs", port=8000):
    print(f"\n[+] Starting local preview server at: http://localhost:{port}/")
    print("    Press Ctrl+C to stop the server.\n")
    try:
        subprocess.run([sys.executable, "-m", "http.server", str(port), "--directory", str(directory)])
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")


def main():
    parser = argparse.ArgumentParser(description="Kosame Maid Blog Archive - Build Pipeline")
    parser.add_argument("--maid-id", type=int, default=1598, help="Maid ID (default: 1598)")
    parser.add_argument("--data-dir", type=str, default="data", help="Scraped data directory")
    parser.add_argument("--output-dir", type=str, default="docs", help="Static site output directory (default: docs)")
    parser.add_argument("--download-images", action="store_true", help="Download all post images locally into data/images/")
    parser.add_argument("--skip-crawl", action="store_true", help="Skip crawling, build site directly from data/")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of posts to crawl (for testing)")
    parser.add_argument("--force", action="store_true", help="Force re-crawling all posts even if cached")
    parser.add_argument("--serve", action="store_true", help="Start local preview server after build")
    parser.add_argument("--port", type=int, default=8000, help="Local preview server port (default: 8000)")

    args = parser.parse_args()

    # Step 1: Crawl
    if not args.skip_crawl:
        print("=" * 60)
        print("  STEP 1: CRAWLING BLOG POSTS (@home cafe API)")
        print("=" * 60)
        run_crawler(
            maid_id=args.maid_id,
            data_dir=args.data_dir,
            download_images=args.download_images,
            force=args.force,
            limit=args.limit
        )
    else:
        print("[*] Skipping crawl step as requested (--skip-crawl)")

    # Step 2: Generate Static Site
    print("\n" + "=" * 60)
    print("  STEP 2: GENERATING STATIC SITE (GitHub Pages Ready)")
    print("=" * 60)
    generate_site(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )

    print("\n" + "=" * 60)
    print(f"  BUILD COMPLETE! Your site is ready in '{args.output_dir}/'")
    print("=" * 60)

    # Step 3: Optional local preview
    if args.serve:
        serve_preview(directory=args.output_dir, port=args.port)


if __name__ == "__main__":
    main()
