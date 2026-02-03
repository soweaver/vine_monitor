import time
import hashlib
import logging
import re
from pathlib import Path
import requests
from monitor_state import monitor_state

# -------------------------
# Path Setup
# -------------------------

# Directory where this file lives (src/)
SRC_DIR = Path(__file__).resolve().parent

# Parent directory (vine_monitor/)
BASE_DIR = SRC_DIR.parent

# Log file and keyword file both in parent directory
LOG_PATH = BASE_DIR / "vine_monitor.log"
KEYWORD_FILE = BASE_DIR / "priority_keywords.txt"

# -------------------------
# Config
# -------------------------

VINE_URL = "https://www.amazon.com/vine/vine-items"
POLL_SECONDS_FAST = 5
POLL_SECONDS_SLOW = 12
QUIET_THRESHOLD_CYCLES = 60

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

# -------------------------
# Logging
# -------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("vine_monitor")

# -------------------------
# Compiled regex
# -------------------------

ASIN_RE = re.compile(r'/dp/([A-Z0-9]{10})')
TITLE_RE = re.compile(r'title="([^"]+)"')

# -------------------------
# Helpers
# -------------------------

def load_priority_keywords():
    """Load keywords from parent directory."""
    if not KEYWORD_FILE.exists():
        log.warning("Keyword file not found: %s", KEYWORD_FILE)
        return []

    keywords = []
    for line in KEYWORD_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if not line or line.startswith("#"):
            continue
        keywords.append(line)

    log.info("Loaded %d priority keywords", len(keywords))
    return keywords


def hash_html(html: str) -> str:
    return hashlib.md5(html.encode("utf-8")).hexdigest()


def extract_relevant_chunk(html: str) -> str:
    """Extract only the Additional Items section for faster parsing."""
    start_marker = "Additional Items"
    end_markers = ["Recommended Items", "Previously Viewed", "Categories"]

    start = html.find(start_marker)
    if start == -1:
        return html

    end = len(html)
    for marker in end_markers:
        idx = html.find(marker, start + len(start_marker))
        if idx != -1:
            end = min(end, idx)

    return html[start:end]


def parse_items(html: str):
    """Extract ASINs and titles from the HTML chunk."""
    chunk = extract_relevant_chunk(html)

    asins = ASIN_RE.findall(chunk)
    titles = TITLE_RE.findall(chunk)

    asin_to_title = {}
    for i, asin in enumerate(asins):
        title = titles[i] if i < len(titles) else ""
        asin_to_title[asin] = title

    return asins, asin_to_title


def has_priority_match(title: str, keywords):
    lower = title.lower()
    return any(k in lower for k in keywords)


# -------------------------
# Main loop
# -------------------------

def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    last_hash = None
    previous_asins = set()
    no_change_cycles = 0
    poll_interval = POLL_SECONDS_FAST

    priority_keywords = load_priority_keywords()

    log.info("Starting optimized Vine monitor")
    log.info("Logging to %s", LOG_PATH)
    log.info("Loading keywords from %s", KEYWORD_FILE)

    while True:
        try:
            resp = session.get(VINE_URL, timeout=20)
            if resp.status_code != 200:
                log.warning("Non-200 status code: %s", resp.status_code)
                time.sleep(poll_interval)
                continue

            html = resp.text
            current_hash = hash_html(html)

            # Skip parsing if HTML is identical
            if current_hash == last_hash:
                no_change_cycles += 1
                if no_change_cycles >= QUIET_THRESHOLD_CYCLES:
                    poll_interval = POLL_SECONDS_SLOW

                monitor_state.record_poll(
                    interval=poll_interval,
                    total_items=len(previous_asins),
                    quiet_cycles=no_change_cycles
                )

                time.sleep(poll_interval)
                continue

            # Reset quiet tracking
            last_hash = current_hash
            no_change_cycles = 0
            poll_interval = POLL_SECONDS_FAST

            # Parse items
            asins, asin_to_title = parse_items(html)
            current_asins = set(asins)

            # Diff
            new_asins = current_asins - previous_asins
            previous_asins = current_asins

            monitor_state.record_poll(
                interval=poll_interval,
                total_items=len(current_asins),
                quiet_cycles=no_change_cycles
            )

            if new_asins:
                for asin in sorted(new_asins):
                    title = asin_to_title.get(asin, "").strip()
                    msg = f"New Additional Item: ASIN={asin}"
                    if title:
                        msg += f" | {title}"
                    log.info(msg)

                    monitor_state.add_new_item(asin, title)

                    if title and has_priority_match(title, priority_keywords):
                        log.info('Priority match found: "%s" (ASIN=%s)', title, asin)
                        monitor_state.add_priority_match(asin, title)

            else:
                log.info("No new items this cycle (%d items total)", len(current_asins))

        except Exception as e:
            log.exception("Error in main loop: %s", e)

        time.sleep(poll_interval)


if __name__ == "__main__":
    main()