"""
AI Trading Core v0.3.1 - Ready to Run on Railway
Backtest Verified: V4 P&L 1771 (17.7%) 126 trades WR 42.1% PF 1.44 DD 5.4%
V5 Allocation: SCB 22.4%, DELTA 22.4%, ADVANC 20.6%, PTTEP 20.6%, PTT 14.0%
"""
import json
import os
from pathlib import Path
from datetime import datetime, timezone

# Import core modules (จาก core/ ที่คุณมี)
from core.config import CONFIG
from core.risk_gate import RiskGate
from core.audit_log import AuditLog
from core.notification_filter import NotificationFilter
from core.profit_based_adjuster import ProfitBasedAdjuster
from core.strategy_adjuster import StrategyAdjuster
from telemetry.event_logger import EventLogger
from telemetry.anomaly_detector import AnomalyDetector

def load_live_config():
    p = Path("data/LIVE_CONFIG_10K.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None

def main():
    print("="*70)
    print("🚀 AI Trading Core v0.3.1 - V5 READY")
    print("="*70)

    live_cfg = load_live_config()
    if live_cfg:
        print(f"✅ Config: {live_cfg.get('version')} Portfolio {live_cfg.get('portfolio')} THB")
    
    # === V5 Allocation จากที่คุณรันได้จริง ===
    real_prices = {"SCB":147.0, "DELTA":248.0, "ADVANC":331.0, "PTTEP":157.0, "PTT":41.0}
    real_atr = {"SCB":2.8, "DELTA":6.5, "ADVANC":4.2, "PTTEP":3.2, "PTT":0.95}
    allocation_v5 = {"SCB":0.224, "DELTA":0.224, "ADVANC":0.206, "PTTEP":0.206, "PTT":0.14}

    # Init core
    Path("logs").mkdir(exist_ok=True)
    audit = AuditLog(path="logs/audit.log")
    risk_gate = RiskGate(portfolio_start_th=1_000_000.0, portfolio_start_us=10_000.0)
    notif_filter = NotificationFilter()
    profit_adjuster = ProfitBasedAdjuster(base_path="data/profit_stats.json")
    event_logger = EventLogger(mode="LIVE", path="logs/events.log")
    anomaly = AnomalyDetector(event_logger)

    print("\n✅ Core loaded: RiskGate, AuditLog, NotificationFilter, ProfitBasedAdjuster")
    print("\n" + "="*70)
    print("Testing V5 Allocation (Portfolio 10k THB)")
    print("="*70)
    
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for sym, pct in allocation_v5.items():
        price = real_prices[sym]
        atr = real_atr[sym]
        max_cost = 10000 * pct
        shares = int(max_cost // price)
        risk_shares, _ = risk_gate.calc_position_size(price, atr, "THB")
        shares = min(shares, risk_shares) if risk_shares>0 else shares
        if shares<1: shares=1
        
        consent, checks = risk_gate.can_enter(sym, shares, price, atr, "THB", date_str)
        status = "✅ PASS" if consent else "❌ REJECT"
        print(f"{sym:8} {pct*100:4.1f}% Price {price:6.1f} ATR {atr:.2f} -> {shares:2} sh Cost {shares*price:.0f}฿ {status}")

    event_logger.log(category="SYSTEM", symbol="SYSTEM", action="STARTUP",
                     payload={"version":"v0.3.1-V5","allocation":allocation_v5}, severity="INFO")
    audit.append(actor="system", action="STARTUP", target="trading_core",
                 payload={"pf":1.44,"wr":42.1,"pnl_pct":17.7}, reason="V4->V5")

    print("\n" + "="*70)
    print("✅ READY - Backtest V4 P&L 1771 (17.7%) WR42.1% PF1.44 DD5.4%")
    print("V5: SCB 22.4% DELTA 22.4% ADVANC 20.6% PTTEP 20.6% PTT 14.0%")
    print("="*70)

    port = int(os.environ.get("PORT", 8000))
    print(f"\nListening on 0.0.0.0:{port} for Railway health check...")

    # Health check server for Railway
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                resp = {
                    "status":"ok",
                    "version":"v0.3.1-V5",
                    "backtest":"V4 PF1.44 WR42.1% +17.7% 126trades",
                    "allocation":allocation_v5,
                    "prices":real_prices,
                    "timestamp":datetime.now(timezone.utc).isoformat()
                }
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode())
            def log_message(self, *a, **k): return
        HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()
    except Exception as e:
        print(f"Server error {e}, fallback sleep...")
        import time
        while True: time.sleep(60)

if __name__ == "__main__":
    main()
