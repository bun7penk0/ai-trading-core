import json
from pathlib import Path

class AuditEntry:
    def __init__(self, payload): 
        self.payload = payload

class AuditLog:
    def __init__(self, path="logs/audit.log"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._entries = []
        # โหลดของเก่าถ้ามี
        if self.path.exists():
            try:
                for line in self.path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        self._entries.append(AuditEntry(json.loads(line)))
            except Exception:
                pass

    def append(self, actor, action, target, payload, reason=""):
        rec = {"actor": actor, "action": action, "target": target, "payload": payload, "reason": reason}
        self._entries.append(AuditEntry(rec))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def all(self):
        return self._entries
