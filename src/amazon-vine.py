import time
import hashlib
import logging
import re
from pathlib import Path
import requests

SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent
LOG_PATH = BASE_DIR / "vine_monitor.log"

VINE_URL = "https://www.amazon.com/vine/vine-items"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("vine_monitor")

# SAME REGEX AS DASHBOARD VERSION
ASIN_RE = re.compile(r'/dp/([A-Z0-9]{10})')
TITLE_RE = re.compile(r'title="([^"]+)"')

def extract_relevant_chunk(html: str) -> str:
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
    chunk = extract_relevant_chunk(html)

    asins = ASIN_RE.findall(chunk)
    titles = TITLE_RE.findall(chunk)

    asin_to_title = {}
    for i, asin in enumerate(asins):
        title = titles[i] if i < len(titles) else ""
        asin_to_title[asin] = title

    return asins, asin_to_title

def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    previous_asins = set()
    last_hash = None

    log.info("Starting Vine Monitor (minimal, dashboard-equivalent parsing)")

    while True:
        try:
            resp = session.get(VINE_URL, timeout=20)
            html = resp.text

            # HASH CHECK
            current_hash = hashlib.md5(html.encode("utf-8")).hexdigest()
            if current_hash == last_hash:
                time.sleep(5)
                continue
            last_hash = current_hash

            # PARSE
            asins, asin_to_title = parse_items(html)
            current_asins = set(asins)

            new_asins = current_asins - previous_asins
            previous_asins = current_asins

            if new_asins:
                for asin in sorted(new_asins):
                    title = asin_to_title.get(asin, "")
                    log.info(f"New Additional Item: ASIN={asin} | {title}")
            else:
                log.info(f"No new items this cycle ({len(current_asins)} items total)")

        except Exception as e:
            log.exception("Error in main loop: %s", e)

        time.sleep(5)

if __name__ == "__main__":
    main()