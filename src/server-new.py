from flask import Flask, jsonify, send_from_directory
from pathlib import Path
from monitor_state import monitor_state

app = Flask(__name__)

# -------------------------
# Path Setup (ABSOLUTE)
# -------------------------

# Directory where server.py lives (src/)
SRC_DIR = Path(__file__).resolve().parent

# Parent directory (where vine_monitor.log and priority_keywords.txt live)
BASE_DIR = SRC_DIR.parent

# Absolute paths
LOG_PATH = BASE_DIR / "vine_monitor.log"
KEYWORD_FILE = BASE_DIR / "priority_keywords.txt"
DASHBOARD_FILE = SRC_DIR / "dashboard.html"

# Debug printout so you can verify paths
print("=== SERVER PATH DEBUG ===")
print("SRC_DIR:", SRC_DIR)
print("BASE_DIR:", BASE_DIR)
print("LOG_PATH:", LOG_PATH)
print("KEYWORD_FILE:", KEYWORD_FILE)
print("DASHBOARD_FILE:", DASHBOARD_FILE)
print("=========================")

# -------------------------
# Routes
# -------------------------

@app.route("/")
def root():
    return send_from_directory(SRC_DIR, "dashboard.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory(SRC_DIR, "dashboard.html")

@app.route("/status")
def status():
    return jsonify({
        "last_poll": monitor_state.last_poll_time,
        "poll_interval": monitor_state.poll_interval,
        "quiet_cycles": monitor_state.quiet_cycles,
        "total_items": monitor_state.total_items
    })

@app.route("/alerts")
def alerts():
    return jsonify(list(monitor_state.recent_new_items))

@app.route("/priority")
def priority():
    return jsonify(list(monitor_state.recent_priority_matches))

@app.route("/keywords")
def keywords():
    if not KEYWORD_FILE.exists():
        return jsonify({"error": f"Keyword file not found: {KEYWORD_FILE}"})
    lines = [
        line.strip()
        for line in KEYWORD_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    return jsonify(lines)

@app.route("/log_tail")
def log_tail():
    if not LOG_PATH.exists():
        return jsonify({"error": f"Log file not found: {LOG_PATH}"})
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()[-200:]
    return jsonify(lines)

# -------------------------
# Run Server
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)