"""AI Trading Core v0.3.1 — Draft (read-only)
main.py V5 - Deploy-Ready
- ThreadingHTTPServer (แก้ #1 blocking)
- #2 SKIP ถ้า shares<1 ไม่ force
- #4 SKIP ถ้า risk_shares<=0 ไม่ fallback
- #5 heartbeat stale -> 503
- #8 LOG_DIR รองรับ Railway Volume
- AllocationValidator pre-flight
- Scheduler every 24h rebalance if trades>=30
- hash 2d1e37ec7288c756
"""
__version__ = "0.3.1-draft"

import os, sys, pathlib
# === FIX PYTHONPATH for Railway ===
ROOT = pathlib.Path(__file__).parent.resolve()
CANDIDATES = [
    ROOT,
    ROOT / "ai_trading_core_v031_draft",
    pathlib.Path("/app"),
    pathlib.Path("/app/ai_trading_core_v031_draft"),
]
for p in CANDIDATES:
    sp = str(p)
    if p.exists() and sp not in sys.path:
        sys.path.insert(0, sp)

import json, hashlib, logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone, date
from pathlib import Path

log = logging.getLogger("main")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# ... (ที่เหลือเหมือนเดิมทุกบรรทัด)
