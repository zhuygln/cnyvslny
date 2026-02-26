"""Constants, term regex patterns, and default paths."""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(ROOT_DIR, "data")
SCHEMA_PATH = os.path.join(DATA_DIR, "schema.json")
CACHE_DIR = os.path.join(ROOT_DIR, ".cache", "crawl")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
TARGETS_PATH = os.path.join(SCRIPT_DIR, "targets.yaml")

# Current year for data file
CURRENT_YEAR = 2026
DATA_FILE = os.path.join(DATA_DIR, f"{CURRENT_YEAR}.jsonl")

# Term detection patterns — order matters for priority
# Allow flexible whitespace, hyphens, and en-dashes between words
TERM_PATTERNS = [
    ("chinese_new_year", re.compile(r"Chinese[\s\-\u2010-\u2015]+New[\s\-\u2010-\u2015]+Year", re.IGNORECASE)),
    ("lunar_new_year", re.compile(r"Lunar[\s\-\u2010-\u2015]+New[\s\-\u2010-\u2015]+Year", re.IGNORECASE)),
    ("spring_festival", re.compile(r"Spring[\s\-\u2010-\u2015]+Festival", re.IGNORECASE)),
    ("spring_festival", re.compile(r"春节")),
]

# Map snake_case keys to schema string values (for single-term entries)
TERM_KEY_TO_STRING = {
    "chinese_new_year": "Chinese New Year",
    "lunar_new_year": "Lunar New Year",
    "spring_festival": "Spring Festival",
}

# Year relevance patterns — filter content to current CNY season
YEAR_RELEVANCE_PATTERNS = [
    re.compile(r"202[56]", re.IGNORECASE),
    re.compile(r"Year\s+of\s+the\s+(Horse|Snake)", re.IGNORECASE),
]

# Rate limiting
DEFAULT_RATE_LIMIT = 1.0  # seconds between requests per domain

# Scoring thresholds
AUTO_ADD_THRESHOLD = 0.55
REVIEW_THRESHOLD = 0.40

# Pagination
USER_AGENT = "cnyvslny-crawler/1.0 (+https://github.com/cnyvslny/cnyvslny)"
REQUEST_TIMEOUT = 15  # seconds

# Contributor name for auto-added entries
CONTRIBUTOR = "crawler"
