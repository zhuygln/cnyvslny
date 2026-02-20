# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**cnyvslny** is a community-maintained dataset tracking how organizations refer to the Chinese New Year / Lunar New Year holiday. It consists of two parts: JSONL data files and an Astro-based website that displays the data.

## Repository Structure

- `data/*.jsonl` — Dataset files (one per year, e.g. `data/2026.jsonl`). Each line is a JSON object validated against `data/schema.json`.
- `scripts/validate.py` — Python validation script (stdlib only, no dependencies). Validates all JSONL files against the schema, checks for duplicates by `(entity_name, source_url)`.
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

Each JSONL entry must conform to `data/schema.json`. Key enum constraints:
- `entity_type`: `company`, `school`, `gov`, `media`, `nonprofit`, `app`, `other`
- `term_used`: `Chinese New Year`, `Lunar New Year`, `Lunar New Year (Chinese New Year)`, `Spring Festival`, `other`
- `context`: `social_post`, `press_release`, `product_ui`, `email`, `event_page`, `website`, `other`
- `captured_on`: `YYYY-MM-DD` format
- `source_url`: must be a valid HTTP/HTTPS URL

Required fields: `entity_name`, `entity_type`, `country_or_region`, `term_used`, `exact_phrase`, `context`, `platform`, `source_url`, `captured_on`, `contributor`. Optional: `notes`, `evidence`.

## Architecture

### Data flow
The Astro site reads JSONL files at build time via `site/src/lib/load-data.ts`, which parses all `data/*.jsonl` files and sorts entries by `captured_on` descending. Entries are serialized to JSON and injected into the page as `window.__CNYVSLNY_DATA__`.

### Client-side rendering
`site/src/scripts/app.ts` handles all client-side interactivity: entries are classified into two columns (CNY vs LNY) based on `term_used`, with infinite scroll pagination (20 items per page via IntersectionObserver) and debounced search filtering.

### Classification logic
An entry is classified as "LNY" column only if `term_used === 'Lunar New Year'`. All other values (`Chinese New Year`, `Spring Festival`, `Lunar New Year (Chinese New Year)`, `other`) go to the "CNY" column. This logic exists in both `site/src/types/entry.ts` (server) and `site/src/scripts/app.ts` (client).

### CI/CD
- **Validate workflow**: Runs `python scripts/validate.py` on PRs that touch `data/**`.
- **Deploy workflow**: Builds the Astro site and deploys to GitHub Pages on push to `main`.
