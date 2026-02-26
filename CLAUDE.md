# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**cnyvslny** is a community-maintained dataset tracking how organizations refer to the Chinese New Year / Lunar New Year holiday. It consists of two parts: JSONL data files and an Astro-based website that displays the data.

## Repository Structure

- `data/*.jsonl` — Dataset files (one per year, e.g. `data/2026.jsonl`). Each line is a JSON object validated against `data/schema.json`.
- `scripts/validate.py` — Python validation script (stdlib only, no dependencies). Validates all JSONL files against the schema, checks for duplicates by `(entity_name, sources[0].url)`.
- `scripts/crawl.py` — CLI entry point for the web crawler.
- `scripts/crawl/` — Crawler package: fetches ~80 target URLs (companies, universities, governments, media, apps, nonprofits), extracts CNY/LNY term usage, scores matches, and auto-adds high-confidence entries to `data/2026.jsonl`.
- `evidence/` — Optional screenshots supporting data entries.
- `site/` — Astro 5 static site with Tailwind CSS, deployed to GitHub Pages.

## Commands

### Validate data
```
python scripts/validate.py
```
Requires Python 3.12+. No pip dependencies. Exits 0 on success, 1 on errors.

### Run crawler
```
pip install requests beautifulsoup4 lxml pyyaml   # one-time setup
python scripts/crawl.py --web-only --verbose       # crawl all targets
python scripts/crawl.py --dry-run --verbose        # preview without writing data
python scripts/crawl.py --max-targets 10           # limit number of targets
```
Requires Python 3.12+. Targets are defined in `scripts/crawl/targets.yaml`. Results above the auto-add threshold (0.55) are written directly to `data/2026.jsonl`; review candidates (0.40–0.55) are written to `scripts/crawl/output/`. The crawler uses browser-like headers, retry with backoff on transient errors (429/5xx), disk caching in `.cache/crawl/`, and respects robots.txt.

### Site development
```
cd site && npm ci        # install dependencies
cd site && npm run dev   # local dev server
cd site && npm run build # production build (outputs to site/dist/)
```
Requires Node 20.

## Data Format

Each JSONL entry must conform to `data/schema.json`. Key fields:

- `entity_name`, `country_or_region`, `exact_phrase`, `platform`, `contributor`: non-empty strings
- `entity_type`: `company`, `school`, `gov`, `media`, `nonprofit`, `app`, `other`
- `term_used`: either a single string (`"Chinese New Year"`, `"Lunar New Year"`, `"Spring Festival"`, `"other"`) or an array of snake_case values (`["chinese_new_year", "lunar_new_year", "spring_festival", "other"]`)
- `context`: `social_post`, `press_release`, `product_ui`, `email`, `event_page`, `website`, `other`
- `sources`: array of `{url, evidence?}` objects (at least one required; `url` must be valid HTTP/HTTPS)
- `captured_on`: `YYYY-MM-DD` format
- `notes`: optional string

## Architecture

### Data flow
The Astro site reads JSONL files at build time via `site/src/lib/load-data.ts`, which parses all `data/*.jsonl` files and sorts entries by `captured_on` descending. Entries are serialized to JSON and injected into the page as `window.__CNYVSLNY_DATA__`.

### Client-side rendering
`site/src/scripts/app.ts` handles all client-side interactivity: entries are classified into two columns (CNY vs LNY) based on `term_used`, with infinite scroll pagination (20 items per page via IntersectionObserver) and debounced search filtering.

### Classification logic
`classifyEntry()` in both `site/src/types/entry.ts` and `site/src/scripts/app.ts` normalizes `term_used` to an array, then uses regex matching: `/chinese/i` → CNY column, `/lunar/i` → LNY column. If an entry matches both (e.g. multi-term), it appears in both columns. All non-lunar terms (`Chinese New Year`, `Spring Festival`, `other`) go to CNY.

### Crawler
- **`scripts/crawl/targets.yaml`**: ~80 targets with entity metadata and specific URLs (search pages, event pages, product pages — not generic homepages).
- **`scripts/crawl/fetcher.py`**: HTTP fetching with browser-like headers (Chrome UA), disk cache, robots.txt compliance, rate limiting, and retry with backoff (up to 2 retries with 3s/6s delays on 429/5xx).
- **`scripts/crawl/extractors/website.py`**: HTML parsing via BeautifulSoup — strips boilerplate tags (`script`, `style`, `nav`, `footer`, `header`, `aside`, `form`, `svg`), then runs term pattern matching.
- **`scripts/crawl/config.py`**: Term regex patterns (flexible whitespace/hyphens), scoring thresholds (`AUTO_ADD_THRESHOLD = 0.55`, `REVIEW_THRESHOLD = 0.40`).
- **`scripts/crawl/pipeline.py`**: Orchestrates fetch → extract → score → route (auto-add / review / discard).
- **`scripts/crawl/scorer.py`**: 5-factor confidence scoring (HTTPS, entity name presence, term count, year relevance, first-party domain).

### CI/CD
- **Validate workflow** (`.github/workflows/validate.yml`): Runs `python scripts/validate.py` on PRs that touch `data/**`.
- **Deploy workflow** (`.github/workflows/deploy.yml`): Builds the Astro site and deploys to GitHub Pages on push to `main`.
