# Web Scraper Plan for cnyvslny

## Goal

Build a scraper pipeline that automatically discovers and collects how organizations publicly refer to the Chinese New Year / Lunar New Year holiday, producing validated JSONL entries ready to merge into `data/`.

---

## Architecture Overview

```
scraper/
├── scrapers/           # Source-specific scraper modules
│   ├── twitter.py      # X/Twitter search scraper
│   ├── google_news.py  # Google News article scraper
│   ├── press_releases.py  # PR Newswire / Business Wire
│   └── web_search.py   # General web search (Google/Bing)
├── pipeline/
│   ├── extractor.py    # Extract term_used, exact_phrase from raw text
│   ├── classifier.py   # Classify entity_type, context, term_used
│   ├── deduplicator.py # Deduplicate against existing JSONL data
│   └── validator.py    # Validate output against data/schema.json
├── output/
│   └── candidates.jsonl  # Scraped entries pending human review
├── config.py           # Search terms, target URLs, API keys config
├── main.py             # CLI entry point orchestrating the pipeline
└── requirements.txt    # Dependencies (requests, beautifulsoup4, etc.)
```

---

## Step-by-Step Implementation Plan

### Step 1: Project scaffolding & configuration (`scraper/config.py`, `scraper/main.py`)

- Create `scraper/` directory at repo root (sibling to `data/`, `site/`)
- Define configuration:
  - **Search queries**: `"Chinese New Year"`, `"Lunar New Year"`, `"Spring Festival"`, `"CNY 2026"`, `"LNY 2026"`
  - **Target year**: Configurable (default: current year)
  - **Output path**: `scraper/output/candidates.jsonl`
  - **Existing data path**: `data/*.jsonl` (for dedup)
  - **Rate limiting**: Configurable delays between requests
- CLI entry point with argparse:
  - `python -m scraper --sources twitter,google_news,web_search --year 2026`
  - `python -m scraper --review` (interactive review mode for candidates)

### Step 2: Web search scraper (`scraper/scrapers/web_search.py`)

Highest-value source. Searches Google/Bing for organizations mentioning the holiday terms.

- **Method**: Use `requests` + BeautifulSoup to parse search results, or use a search API (SerpAPI / Bing Web Search API)
- **Queries**:
  - `"Lunar New Year" site:twitter.com OR site:instagram.com 2026`
  - `"Chinese New Year" press release 2026`
  - `"Spring Festival" company announcement 2026`
  - Company-specific: iterate Fortune 500 list + `"Lunar New Year" OR "Chinese New Year"`
- **Output per result**: URL, page title, snippet text
- **Rate limiting**: 2-5 second delays between requests; respect robots.txt

### Step 3: Google News / press release scraper (`scraper/scrapers/google_news.py`, `scraper/scrapers/press_releases.py`)

- **Google News**: Search for `"Lunar New Year"` and `"Chinese New Year"` in news articles
  - Parse Google News RSS feeds: `https://news.google.com/rss/search?q=...`
  - Extract: article URL, title, publication date, source name
- **PR Newswire / Business Wire / GlobeNewsWire**:
  - Search their sites for holiday-related press releases
  - These are high-quality sources with clear entity attribution
  - Parse: company name, release title, date, URL

### Step 4: Social media scraper (`scraper/scrapers/twitter.py`)

- **X/Twitter**: Search for corporate accounts posting about the holiday
  - Use Twitter/X search API or Nitter instances for public posts
  - Filter by verified/business accounts to focus on organizations
  - Search terms: `"Happy Lunar New Year" from:verified`, `"Chinese New Year" from:verified`
- **Output**: tweet URL, account name, tweet text, date

### Step 5: Extraction & classification pipeline (`scraper/pipeline/`)

#### `extractor.py` — Field extraction from raw scraped data
- **entity_name**: Extract organization name from page metadata, social account name, or press release byline
- **exact_phrase**: Find the specific sentence/phrase containing the holiday term using regex patterns:
  - `r"[^.]*(?:Chinese New Year|Lunar New Year|Spring Festival)[^.]*\."`
- **platform**: Extract domain from source URL (e.g., `twitter.com`, `apple.com`)
- **captured_on**: Use today's date in `YYYY-MM-DD` format
- **source_url**: The scraped URL

#### `classifier.py` — Enum field classification
- **term_used**: Pattern match against the exact_phrase:
  - Contains "Chinese New Year" → `"Chinese New Year"` (or `"chinese_new_year"` in array form)
  - Contains "Lunar New Year" → `"Lunar New Year"` (or `"lunar_new_year"`)
  - Contains both → array `["chinese_new_year", "lunar_new_year"]`
  - Contains "Spring Festival" → `"Spring Festival"`
  - Otherwise → `"other"`
- **entity_type**: Heuristic classification:
  - Known company domains / Fortune 500 list → `"company"`
  - `.edu` domains → `"school"`
  - `.gov` domains → `"gov"`
  - News outlets list → `"media"`
  - Otherwise → `"other"` (flag for human review)
- **context**: Classify based on source:
  - Twitter/Instagram/Facebook → `"social_post"`
  - PR Newswire/BusinessWire → `"press_release"`
  - App stores, product pages → `"product_ui"`
  - News articles → `"website"`
  - Otherwise → `"other"`
- **country_or_region**: Attempt to determine from:
  - TLD (`.co.uk` → UK, `.cn` → China)
  - Known entity mapping (Fortune 500 → US)
  - Default to `"US"` with flag for human review

### Step 6: Deduplication (`scraper/pipeline/deduplicator.py`)

- Load all existing entries from `data/*.jsonl`
- Build a set of `(entity_name_normalized, source_url)` tuples
- For each candidate, check:
  1. Exact duplicate: same entity_name + same source URL → skip
  2. Same entity, different URL: keep (new source for same org)
  3. Fuzzy entity name matching (Levenshtein or normalized comparison) to catch variants like "Apple Inc." vs "Apple"
- Output: deduplicated candidates only

### Step 7: Validation (`scraper/pipeline/validator.py`)

- Re-use the validation logic from `scripts/validate.py`
- Validate each candidate entry against `data/schema.json`
- Flag entries that fail validation with specific error messages
- Separate valid entries from entries needing fixes

### Step 8: Human review interface (`scraper/main.py --review`)

Since scraped data needs human verification before merging:

- Interactive CLI review mode:
  - Display each candidate entry formatted nicely
  - Allow: **accept**, **edit** (modify fields), **reject**, **skip**
  - Accepted entries are appended to the appropriate `data/YYYY.jsonl` file
- Generate a summary report:
  - Total candidates found
  - Breakdown by term_used, entity_type, context
  - Duplicates filtered out
  - Entries accepted vs rejected

---

## Dependencies (`scraper/requirements.txt`)

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
```

No heavy frameworks. Optionally:
- `selenium` or `playwright` — only if JavaScript-rendered pages are needed
- `python-Levenshtein` — for fuzzy entity name matching in dedup

---

## Target Sources (Priority Order)

| Priority | Source | Expected Yield | Effort |
|----------|--------|---------------|--------|
| 1 | Google News RSS | High — many orgs covered in news | Low |
| 2 | PR Newswire / Business Wire | High — direct company statements | Low |
| 3 | Fortune 500 websites | High — authoritative companies | Medium |
| 4 | X/Twitter corporate accounts | Medium — social posts | Medium |
| 5 | University websites (.edu) | Medium — event pages | Medium |
| 6 | Government sites (.gov) | Low-Medium — official statements | Medium |

---

## Scraping Ethics & Safeguards

- **Respect robots.txt**: Check and honor robots.txt for every domain
- **Rate limiting**: Minimum 2-second delay between requests to same domain
- **User-Agent**: Identify as a research bot with contact info
- **No authentication bypass**: Only scrape publicly accessible pages
- **No CAPTCHA solving**: Skip pages requiring CAPTCHA
- **Caching**: Cache raw HTML to avoid re-fetching during development
- **contributor field**: Set to `"scraper"` to distinguish from manual entries

---

## Implementation Order

1. **Scaffolding**: `config.py`, `main.py`, `requirements.txt`, directory structure
2. **Google News RSS scraper**: Quickest to implement, highest ROI
3. **Extraction pipeline**: `extractor.py` + `classifier.py`
4. **Deduplicator**: Load existing data, filter candidates
5. **Validator**: Reuse schema validation logic
6. **Review CLI**: Interactive accept/reject workflow
7. **Web search scraper**: Broader coverage
8. **Press release scraper**: PR Newswire, Business Wire
9. **Social media scraper**: Twitter/X corporate accounts
10. **Fortune 500 targeted scraper**: Iterate known companies

---

## Expected Output

Running the full pipeline should produce `scraper/output/candidates.jsonl` with entries like:

```json
{"entity_name": "Nike", "entity_type": "company", "country_or_region": "US", "term_used": "Lunar New Year", "exact_phrase": "Celebrate Lunar New Year with Nike's latest collection", "context": "website", "platform": "nike.com", "captured_on": "2026-02-23", "contributor": "scraper", "sources": [{"url": "https://www.nike.com/lunar-new-year"}]}
```

After human review, accepted entries get appended to `data/2026.jsonl` and validated with `python scripts/validate.py`.
