from flask import Flask, send_from_directory
from pathlib import Path

app = Flask(__name__)

# Directory where server.py lives
SRC_DIR = Path(__file__).resolve().parent

# Parent directory where vine_monitor.log lives
BASE_DIR = SRC_DIR.parent

LOG_PATH = BASE_DIR / "vine_monitor.log"

@app.route("/")
def root():
    return send_from_directory(SRC_DIR, "index.html")

@app.route("/log")
def log():
    if not LOG_PATH.exists():
        return "Log file not found.", 404
    return LOG_PATH.read_text(encoding="utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)