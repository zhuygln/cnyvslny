#!/usr/bin/env python3
"""CLI entry point for the cnyvslny web crawler.

Usage:
    python scripts/crawl.py                        # Full crawl
    python scripts/crawl.py --dry-run --verbose    # Preview without writing
    python scripts/crawl.py --entity "Apple"       # Single entity
    python scripts/crawl.py --twitter-only         # Twitter only
    python scripts/crawl.py --web-only             # Websites only
    python scripts/crawl.py --auto-threshold 0.60  # Lower bar for auto-add
"""

import argparse
import logging
import sys

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from crawl.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Crawl targeted websites and Twitter for CNY/LNY terminology",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview candidates without writing to data files",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose/debug logging",
    )
    parser.add_argument(
        "--entity", type=str, default=None,
        help="Filter to a single entity by name (substring match)",
    )
    parser.add_argument(
        "--web-only", action="store_true",
        help="Only crawl website URLs, skip Twitter",
    )
    parser.add_argument(
        "--twitter-only", action="store_true",
        help="Only search Twitter, skip website URLs",
    )
    parser.add_argument(
        "--max-targets", type=int, default=None,
        help="Limit number of targets to process",
    )
    parser.add_argument(
        "--auto-threshold", type=float, default=0.70,
        help="Minimum confidence score for auto-adding (default: 0.70)",
    )
    parser.add_argument(
        "--review-threshold", type=float, default=0.40,
        help="Minimum confidence score for review queue (default: 0.40)",
    )
    parser.add_argument(
        "--targets-file", type=str, default=None,
        help="Path to targets YAML file (default: scripts/crawl/targets.yaml)",
    )

    args = parser.parse_args()

    if args.web_only and args.twitter_only:
        parser.error("Cannot use both --web-only and --twitter-only")

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    result = run_pipeline(
        targets_path=args.targets_file,
        entity_filter=args.entity,
        web_only=args.web_only,
        twitter_only=args.twitter_only,
        dry_run=args.dry_run,
        verbose=args.verbose,
        max_targets=args.max_targets,
        auto_threshold=args.auto_threshold,
        review_threshold=args.review_threshold,
    )

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Print summary
    print("\n--- Crawl Summary ---")
    print(f"  Targets processed: {result['targets_processed']}")
    print(f"  URLs fetched:      {result['urls_fetched']}")
    print(f"  Auto-added:        {result['auto_added']}")
    print(f"  Review queue:      {result['review_queue']}")
    print(f"  Discarded:         {result['discarded']}")
    print(f"  Skipped (dedup):   {result['skipped_dedup']}")
    if result['errors']:
        print(f"  Errors:            {len(result['errors'])}")
        for err in result['errors']:
            print(f"    - {err}")


if __name__ == "__main__":
    main()
