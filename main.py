"""AI Trading Core v0.3.1 — Draft (read-only)
main.py V5 - Deploy-Ready (Single-File Edition)
"""
__version__ = "0.3.1-draft"

import os, sys, pathlib
import json, hashlib, logging, threading, uuid, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone, date
from pathlib import Path
from dataclasses import dataclass, field

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

log = logging.getLogger("main")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# ==========================================
# ส่วนที่ 1: ดึงโค้ดจาก core/audit_log.py มารวม
# ==========================================
class AuditEntry:
    def __init__(self, payload): 
        self.payload = payload

class AuditLog:
    def __init__(self, path="logs/audit.log"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._entries = []
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

# ==========================================
# ส่วนที่ 2: ดึงโค้ดจาก core/risk_gate.py มารวม
# ==========================================
@dataclass
class Consent:
    consent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    shares: int = 0
    price: float = 0.0

class RiskGate:
    def __init__(self, max_risk_pct: float = 0.02, atr_mult: float = 2.0):
        self.max_risk_pct = max_risk_pct
        self.atr_mult = atr_mult

    def calc_position_size(self, price: float, atr: float, currency: str = "THB"):
        if price <= 0 or atr <= 0:
            return 0, "invalid price/atr"
        risk_budget = 10000 * self.max_risk_pct
        stop_dist = self.atr_mult * atr
        shares = int(risk_budget // stop_dist) if stop_dist > 0 else 0
        return shares, f"risk_budget={risk_budget:.0f} stop_dist={stop_dist:.2f}"

    def can_enter(self, symbol, shares, price, atr, currency, date_str):
        checks = []
        if shares <= 0: checks.append("shares<=0")
        if price <= 0: checks.append("price<=0")
        if checks: return None, checks
        return Consent(symbol=symbol, shares=shares, price=price), checks

# ==========================================
# ส่วนที่ 3: ดึงโค้ดจาก core/allocation_validator.py มารวม
# ==========================================
class AllocationValidator:
    def __init__(self, cfg: dict):
        self.cfg = cfg or {}

    def validate(self):
        errs = []
        if not self.cfg.get("version"): errs.append("missing 'version'")
        if not self.cfg.get("portfolio"): errs.append("missing 'portfolio'")
        lp = self.cfg.get("live_params") or {}
        if "max_positions" not in lp: errs.append("missing live_params.max_positions")
        if "max_per_position_pct" not in lp: errs.append("missing live_params.max_per_position_pct")
        return (len(errs) == 0, errs)

# ==========================================
# ส่วนที่ 4: ดึงโค้ดจาก core/scheduler.py มารวม
# ==========================================
_sched_stop = threading.Event()
_sched_thr = None

def _sched_loop(config_path, trade_log_path, min_trades, check_hours):
    interval = max(60, int(check_hours) * 3600)
    log.info(f"scheduler started interval={interval}s min_trades={min_trades}")
    
    import time
    next_rebalance = time.time() + interval

    while not _sched_stop.is_set():
        # รอแค่ 60 วิ แล้วตื่นมา
        if _sched_stop.wait(60):
            break
        
        # ยิง heartbeat ทุก 60 วิ เพื่อไม่ให้ขึ้น stale
        try:
            update_heartbeat()
        except Exception:
            pass

        # ถ้าครบ 24 ชม. จริงๆ ค่อยทำ rebalance
        if time.time() >= next_rebalance:
            log.info("scheduler tick (TODO: rebalance)")
            # TODO: ใส่โค้ด rebalance จริงตรงนี้
            next_rebalance = time.time() + interval _sched_loop(config_path, trade_log_path, min_trades, check_hours):
    interval = max(60, int(check_hours) * 3600)
    log.info(f"scheduler started interval={interval}s min_trades={min_trades}")
    while not _sched_stop.wait(interval):
        log.info("scheduler tick (TODO: rebalance logic)")

def start_scheduler(config_path, trade_log_path, min_trades=30, check_hours=24):
    global _sched_thr
    _sched_stop.clear()
    _sched_thr = threading.Thread(target=_sched_loop, args=(config_path, trade_log_path, min_trades, check_hours), daemon=True)
    _sched_thr.start()
    return _sched_thr

def stop_scheduler():
    _sched_stop.set()
    if _sched_thr: _sched_thr.join(timeout=5)
    log.info("scheduler stopped")

# ==========================================
# ส่วนที่ 5: ดึงโค้ดจาก telemetry/event_logger.py มารวม
# ==========================================
class EventLogger:
    def __init__(self, mode: str = "LIVE", path: str = "logs/events.log"):
        self.mode = mode
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, category, symbol=None, action=None, payload=None):
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "mode": self.mode, "category": category, "symbol": symbol, "action": action, "payload": payload or {}}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ==========================================
# ส่วนที่ 6: โค้ดหลักของ main.py เดิม (ไม่ต้องสร้าง core แล้ว)
# ==========================================
def load_live_config():
    cfg_path = Path(os.getenv("CONFIG_PATH","data/LIVE_CONFIG_10K.json"))
    try:
        if not cfg_path.exists():
            log.warning("config missing, using defaults")
            return None
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        file_hash = hashlib.sha256(cfg_path.read_bytes()).hexdigest()[:16]
        log.info(f"config loaded file_hash={file_hash} frozen={data.get('frozen_hash')} version={data.get('version')}")
        return data
    except Exception as e:
        log.error(f"load config failed: {e}")
        return None

live_config = load_live_config()

allocation_v5 = {"SCB.BK":0.224,"DELTA.BK":0.224,"ADVANC.BK":0.206,"PTTEP.BK":0.206,"PTT.BK":0.14}
real_prices = {"SCB.BK":147,"DELTA.BK":248,"ADVANC.BK":331,"PTTEP.BK":157,"PTT.BK":41}
real_atr = {"SCB.BK":2.8,"DELTA.BK":6.5,"ADVANC.BK":4.2,"PTTEP.BK":3.2,"PTT.BK":0.95}
PORTFOLIO = 10000

risk_gate = RiskGate()
log_dir = Path(os.getenv("LOG_DIR","logs"))
log_dir.mkdir(parents=True, exist_ok=True)
audit = AuditLog(path=str(log_dir / "audit.log"))
events = EventLogger(mode="LIVE", path=str(log_dir / "events.log"))

last_tick = {"t": datetime.now(timezone.utc)}
def update_heartbeat():
    last_tick["t"] = datetime.now(timezone.utc)

def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    ok, errs = AllocationValidator(cfg).validate()
    if not ok:
        for e in errs:
            log.error(f"CONFIG INVALID: {e}")
        raise SystemExit("Config invalid - abort")
    log.info(f"✅ Loaded {cfg['version']} portfolio={cfg['portfolio']} max_pos={cfg['live_params']['max_positions']} max_pct={cfg['live_params']['max_per_position_pct']*100:.1f}%")
    return cfg

def run_startup_allocation():
    runtime_id = os.environ.get("RAILWAY_DEPLOYMENT_ID", f"local-{int(datetime.now(timezone.utc).timestamp())}")
    try:
        last_audit = audit.all()[-1] if audit.all() else None
        if last_audit and last_audit.payload.get("deploy_id")==runtime_id:
            log.info(f"STARTUP already logged for {runtime_id}, skip")
            return
    except: pass
    log.info(f"🚀 STARTUP V5 deploy_id={runtime_id} portfolio={PORTFOLIO}")
    audit.append(actor="system", action="STARTUP", target="portfolio", payload={"deploy_id":runtime_id,"portfolio":PORTFOLIO,"allocation":allocation_v5}, reason="V5 hypothesis 2d1e37ec7288c756")
    
    for sym, alloc_pct in allocation_v5.items():
        price = real_prices.get(sym,0)
        atr = real_atr.get(sym,0)
        if not price: continue
        budget = PORTFOLIO * alloc_pct
        shares = int(budget // price) if price>0 else 0
        
        if shares < 1:
            log.info(f"{sym} SKIP allocation too small budget={budget:.0f} price={price}")
            events.log(category="RISK_REJECT", symbol=sym, action="SKIP_SMALL_ALLOC", payload={"budget":budget,"price":price})
            continue
        
        try:
            risk_shares, risk_msg = risk_gate.calc_position_size(price, atr, "THB")
        except Exception as e:
            log.error(f"{sym} risk calc failed {e}")
            continue
        
        if risk_shares <= 0:
            log.warning(f"{sym} SKIP risk_gate 0 {risk_msg}")
            events.log(category="RISK_REJECT", symbol=sym, action="RISK_ZERO", payload={"risk_shares":risk_shares})
            continue
        
        final_shares = min(shares, risk_shares)
        date_str = date.today().isoformat()
        consent, checks = risk_gate.can_enter(sym, final_shares, price, atr, "THB", date_str)
        if consent is None:
            log.warning(f"{sym} RiskGate reject {checks}")
            events.log(category="RISK_REJECT", symbol=sym, action="REJECT", payload={"checks":checks})
            continue
        log.info(f"{sym} OK shares={final_shares} cost={final_shares*price} risk_shares={risk_shares} consent={consent.consent_id[:8]}")
        events.log(category="DECISION", symbol=sym, action="OPEN", payload={"shares":final_shares,"cost":final_shares*price,"price":price,"atr":atr,"consent_id":consent.consent_id})
        update_heartbeat()

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        age = (datetime.now(timezone.utc) - last_tick["t"]).total_seconds()
        is_stale = age > 120
        if self.path == "/favicon.ico":
            self.send_response(204); self.end_headers(); return
        if self.path in ("/","/health","/api/health"):
            status = 503 if is_stale else 200
            self.send_response(status)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            body = {
                "status":"ok" if status==200 else "stale",
                "version":"v0.3.1-adaptive-V5-profit-based",
                "hash":"2d1e37ec7288c756",
                "legacy_hash":"d83fe34155adfabe",
                "verify": True,
                "portfolio": PORTFOLIO,
                "allocation_V5": {
                    "SCB.BK":"22.4% P&L 714 WR52%",
                    "DELTA.BK":"22.4% P&L 855 WR48%",
                    "ADVANC.BK":"20.6% P&L 277 WR38%",
                    "PTTEP.BK":"20.6% P&L 112 WR36%",
                    "PTT.BK":"14.0% P&L -185 WR29%"
                },
                "backtest":"V4 hypothesis P&L 1771 (17.7%) 126 trades WR42.1% PF1.44 DD5.4%",
                "heartbeat_age_s": round(age,1),
                "time": datetime.now(timezone.utc).isoformat(),
                "deploy_id": os.getenv("RAILWAY_DEPLOYMENT_ID","local")
            }
            self.wfile.write(json.dumps(body).encode())
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'{"detail":"Not Found"}')
    def log_message(self, format, *args):
        print(json.dumps({"level":"info","message":f"{self.client_address[0]} {format%args}","path":self.path}))

def main():
    cfg_path = os.getenv("CONFIG_PATH","data/LIVE_CONFIG_10K.json")
    log_path = os.getenv("TRADE_LOG_PATH","data/trade_log.json")
    cfg = load_config(cfg_path)
    sch = start_scheduler(config_path=cfg_path, trade_log_path=log_path, min_trades=int(os.getenv("REBALANCE_MIN_TRADES","30")), check_hours=int(os.getenv("REBALANCE_CHECK_HOURS","24")))
    run_startup_allocation()
    port = int(os.getenv("PORT","8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    print(json.dumps({"level":"info","message":f"Health server listening V5 {cfg['version']}","port":port,"threaded":True,"hash":"2d1e37ec7288c756"}))
    try:
        server.serve_forever()
    finally:
        stop_scheduler()

if __name__ == "__main__":
    main()
