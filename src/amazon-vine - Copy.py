import time
import requests
import re
from pathlib import Path

# Paths
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent
LOG_PATH = BASE_DIR / "vine_monitor.log"

URL = "https://www.amazon.com/vine/vine-items"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

# Updated patterns for current Amazon Vine HTML
#ASIN_RE = re.compile(r'data-asin="([A-Z0-9]{10})"')
#TITLE_RE = re.compile(r'data-asin-title="([^"]+)"')

ASIN_RE = re.compile(r'/dp/([A-Z0-9]{10})')
TITLE_RE = re.compile(r'title="([^"]+)"')


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(msg)

def main():
    previous_asins = set()

    log("Starting Vine Monitor")

    while True:
        try:
            resp = requests.get(URL, headers=HEADERS, timeout=20)
            html = resp.text

            # Extract ASINs and titles using updated patterns
            asins = ASIN_RE.findall(html)
            titles = TITLE_RE.findall(html)

            asin_to_title = {}
            for i, asin in enumerate(asins):
                title = titles[i] if i < len(titles) else ""
                asin_to_title[asin] = title

            current_asins = set(asins)
            new_asins = current_asins - previous_asins
            previous_asins = current_asins

            for asin in new_asins:
                title = asin_to_title.get(asin, "")
                log(f"New Additional Item: ASIN={asin} | {title}")

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(5)

if __name__ == "__main__":
    main()