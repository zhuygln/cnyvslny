# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**cnyvslny** is a community-maintained dataset tracking how organizations refer to the Chinese New Year / Lunar New Year holiday. It consists of two parts: JSONL data files and an Astro-based website that displays the data.

## Repository Structure

- `data/*.jsonl` — Dataset files (one per year, e.g. `data/2026.jsonl`). Each line is a JSON object validated against `data/schema.json`.
- `scripts/validate.py` — Python validation script (stdlib only, no dependencies). Validates all JSONL files against the schema, checks for duplicates by `(entity_name, sources[0].url)`.
- `evidence/` — Optional screenshots supporting data entries.
- `site/` — Astro 5 static site with Tailwind CSS, deployed to GitHub Pages.

## Commands

### Validate data
```
python scripts/validate.py
```
Requires Python 3.12+. No pip dependencies. Exits 0 on success, 1 on errors.

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

### CI/CD
- **Validate workflow** (`.github/workflows/validate.yml`): Runs `python scripts/validate.py` on PRs that touch `data/**`.
- **Deploy workflow** (`.github/workflows/deploy.yml`): Builds the Astro site and deploys to GitHub Pages on push to `main`.
