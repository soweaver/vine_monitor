# monitor_state.py

from collections import deque
from datetime import datetime

class MonitorState:
    def __init__(self):
        self.last_poll_time = None
        self.poll_interval = None
        self.quiet_cycles = 0
        self.total_items = 0

        # Keep recent events
        self.recent_new_items = deque(maxlen=50)
        self.recent_priority_matches = deque(maxlen=50)

    def record_poll(self, interval, total_items, quiet_cycles):
        self.last_poll_time = datetime.now().isoformat(timespec="seconds")
        self.poll_interval = interval
        self.total_items = total_items
        self.quiet_cycles = quiet_cycles

    def add_new_item(self, asin, title):
        self.recent_new_items.appendleft({
            "time": datetime.now().isoformat(timespec="seconds"),
            "asin": asin,
            "title": title
        })

    def add_priority_match(self, asin, title):
        self.recent_priority_matches.appendleft({
            "time": datetime.now().isoformat(timespec="seconds"),
            "asin": asin,
            "title": title
        })

monitor_state = MonitorState()