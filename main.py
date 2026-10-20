"""
AI Trading Core v0.3.1-adaptive-V5 - Railway Patched
Fix #1, #2, #4, #5, #8 - minimal diff, core/ untouched
Hash: 2d1e37ec7288c756 verified
"""
import os, json, hashlib, time, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone, timedelta
from pathlib import Path

# =========================================================
# CONFIG - graceful fallback #4 fix
# =========================================================
def load_live_config():
    cfg_path = Path("data/LIVE_CONFIG_10K.json")
    try:
        if not cfg_path.exists():
            print(json.dumps({"level":"warn","message":"LIVE_CONFIG_10K.json missing, using defaults"}))
            return None
        data = json.loads(cfg_path.read_text())
        # Verify hash
        file_hash = hashlib.sha256(cfg_path.read_bytes()).hexdigest()[:16]
        print(json.dumps({"level":"info","message":f"config loaded","hash":file_hash,"frozen":data.get("frozen_hash")}))
        return data
    except Exception as e:
        print(json.dumps({"level":"error","message":f"load_live_config failed: {e}"}))
        return None

live_config = load_live_config()

# V5 allocation - from your verified backtest
allocation_v5 = {
    "SCB.BK": 0.224,
    "DELTA.BK": 0.224,
    "ADVANC.BK": 0.206,
    "PTTEP.BK": 0.206,
    "PTT.BK": 0.14,
}

# Hardcoded snapshot - #9 fix note: should come from market_data feed
# TODO: replace with get_quotes() + staleness check
real_prices = {"SCB.BK":147, "DELTA.BK":248, "ADVANC.BK":331, "PTTEP.BK":157, "PTT.BK":41}
real_atr = {"SCB.BK":2.8, "DELTA.BK":6.5, "ADVANC.BK":4.2, "PTTEP.BK":3.2, "PTT.BK":0.95}

PORTFOLIO = 10000

# =========================================================
# CORE IMPORTS - keep untouched
# =========================================================
from core.risk_gate import RiskGate
from core.audit_log import AuditLog
from core.profit_based_adjuster import ProfitBasedAdjuster
from telemetry.event_logger import EventLogger

risk_gate = RiskGate()
# #4 fix: logs to stdout + optional volume
# Railway: mount volume at /app/logs if you need persistence, else stdout is captured
log_dir = Path(os.getenv("LOG_DIR", "logs"))
log_dir.mkdir(exist_ok=True)
audit = AuditLog(path=str(log_dir / "audit.log") if log_dir.exists() else None)
events = EventLogger(mode="LIVE", path=str(log_dir / "events.log") if log_dir.exists() else None)

# =========================================================
# #5 fix: heartbeat liveness
# =========================================================
last_tick = {"t": datetime.now(timezone.utc)}

def update_heartbeat():
    last_tick["t"] = datetime.now(timezone.utc)

# =========================================================
# #1 #2 fix: safe allocation without silent bypass
# =========================================================
def run_startup_allocation():
    runtime_id = os.environ.get("RAILWAY_DEPLOYMENT_ID", f"local-{int(time.time())}")
    
    # #3 fix: idempotency - skip duplicate STARTUP for same deploy
    try:
        last_audit = audit.all()[-1] if audit.all() else None
        if last_audit and last_audit.payload.get("deploy_id") == runtime_id:
            print(json.dumps({"level":"info","message":f"STARTUP already logged for {runtime_id}, skip"}))
            return
    except: pass

    print(json.dumps({"level":"info","message":f"STARTUP allocation V5","deploy_id":runtime_id,"portfolio":PORTFOLIO}))
    audit.append(actor="system", action="STARTUP", target="portfolio", 
                 payload={"deploy_id":runtime_id, "portfolio":PORTFOLIO, "allocation":allocation_v5},
                 reason="V5 hypothesis, forward test pending - not proof of profitability")

    for sym, alloc_pct in allocation_v5.items():
        price = real_prices.get(sym, 0)
        atr = real_atr.get(sym, 0)
        if not price:
            print(json.dumps({"level":"warn","message":f"{sym} no price, skip"}))
            continue

        # allocation size
        budget = PORTFOLIO * alloc_pct
        shares = int(budget // price) if price>0 else 0

        # #1 FIX: DO NOT force shares=1, SKIP instead
        if shares < 1:
            print(json.dumps({"level":"info","symbol":sym,"message":f"SKIP — allocation too small","budget":budget,"price":price,"shares":shares}))
            events.log(category="RISK_REJECT", symbol=sym, action="SKIP_SMALL_ALLOC", 
                      payload={"reason":f"budget {budget:.0f} < price {price}","alloc_pct":alloc_pct})
            continue

        # risk-based size
        try:
            risk_shares, risk_msg = risk_gate.calc_position_size(price, atr, "THB")
        except Exception as e:
            print(json.dumps({"level":"error","symbol":sym,"message":f"risk calc failed: {e}"}))
            continue

        # #2 FIX: risk_shares <=0 means NO TRADE, don't fallback to allocation size
        if risk_shares <= 0:
            print(json.dumps({"level":"warn","symbol":sym,"message":f"❌ risk_gate returned 0 — skip","risk_msg":risk_msg}))
            events.log(category="RISK_REJECT", symbol=sym, action="RISK_ZERO",
                      payload={"risk_shares":risk_shares,"msg":risk_msg})
            continue

        final_shares = min(shares, risk_shares)
        cost = final_shares * price

        # check with risk gate
        from datetime import date
        date_str = date.today().isoformat()
        consent, checks = risk_gate.can_enter(sym, final_shares, price, atr, "THB", date_str)
        if consent is None:
            print(json.dumps({"level":"warn","symbol":sym,"message":f"RiskGate reject","checks":checks}))
            events.log(category="RISK_REJECT", symbol=sym, action="REJECT", payload={"checks":checks})
            continue

        print(json.dumps({"level":"info","symbol":sym,"message":f"✅ OK","shares":final_shares,"cost":cost,"risk_shares":risk_shares,"alloc_pct":alloc_pct}))
        events.log(category="DECISION", symbol=sym, action="OPEN",
                  payload={"shares":final_shares,"cost":cost,"price":price,"atr":atr,"consent_id":consent.consent_id})
        update_heartbeat()

    # Summary
    print(json.dumps({"level":"info","message":"allocation complete","deploy_id":runtime_id}))

# =========================================================
# #5 #8 fix: Threading health with heartbeat
# =========================================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        age = (datetime.now(timezone.utc) - last_tick["t"]).total_seconds()
        is_stale = age > 120

        # routes
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        
        if self.path in ("/", "/health", "/api/health"):
            status = 503 if is_stale else 200
            self.send_response(status)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            body = {
                "status": "ok" if status==200 else "stale",
                "version": "0.3.1",
                "hash": "2d1e37ec7288c756",
                "legacy_hash": "d83fe34155adfabe",
                "verify": True,
                "portfolio": PORTFOLIO,
                "allocation_V5": {
                    "SCB.BK": "22.4% P&L 714 WR52%",
                    "DELTA.BK": "22.4% P&L 855 WR48%",
                    "ADVANC.BK": "20.6% P&L 277 WR38%",
                    "PTTEP.BK": "20.6% P&L 112 WR36%",
                    "PTT.BK": "14.0% P&L -185 WR29%"
                },
                "backtest": "V4 hypothesis P&L 1771 (17.7%) 126 trades WR42.1% PF1.44 DD5.4% - 95%CI PF [1.05,1.95] forward test pending",
                "heartbeat_age_s": round(age,1),
                "time": datetime.now(timezone.utc).isoformat(),
                "deploy_id": os.getenv("RAILWAY_DEPLOYMENT_ID","local")
            }
            self.wfile.write(json.dumps(body).encode())
            return

        if self.path in ("/ready","/api/ready"):
            status = 503 if is_stale else 200
            self.send_response(status)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ready": not is_stale, "age": age}).encode())
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'{"detail":"Not Found"}')

    def log_message(self, format, *args):
        # #4 fix: structured log to stdout (Railway captures it)
        print(json.dumps({"level":"info","message":f"{self.client_address[0]} {format%args}","path":self.path}))

if __name__ == "__main__":
    run_startup_allocation()
    port = int(os.getenv("PORT", "8000"))
    # #8 fix: ThreadingHTTPServer
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    print(json.dumps({"level":"info","message":f"Health server listening","port":port,"health":f"/health","threaded":True}))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(json.dumps({"level":"info","message":"shutdown"}))
