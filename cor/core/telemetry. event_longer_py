import json
from pathlib import Path
from datetime import datetime, timezone

class EventLogger:
    def __init__(self, mode: str = "LIVE", path: str = "logs/events.log"):
        self.mode = mode
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, category, symbol=None, action=None, payload=None):
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "mode": self.mode, "category": category, "symbol": symbol, "action": action, "payload": payload or {}}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
