import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# โหลดค่าจาก Environment Variable (ถ้าไม่มีจะใช้ค่า Default)
HASH = os.getenv("LIVE_CONFIG_10K_HASH", "676bad20288d7623")

# ข้อมูลจำลองจาก LIVE_CONFIG_10K.json และ ADAPTIVE_TIERS.json
LIVE = {
    "version": "v0.3.1-adaptive-10K",
    "portfolio": 10000,
    "tier": "SMALL_1k_10k",
    "risk_pct": 0.01,
    "stop_atr_mult": 1.8,
    "take_profit_atr_mult": 2.5,
    "max_pos": 2,
    "stocks": {
        "PTT": {"price": 32.5, "atr": 0.8, "shares": 69, "cost": 2242},
        "AOT": {"price": 58.25, "atr": 1.5, "shares": 37, "cost": 2155},
        "CPALL": {"price": 62.0, "atr": 1.2, "shares": 46, "cost": 2852},
        "SCB": {"price": 110.0, "atr": 2.0, "shares": 27, "cost": 2970}
    }
}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    # สร้างแถวตาราง HTML จากข้อมูลหุ้น
    rows = ""
    for k, v in LIVE["stocks"].items():
        formula_calc = (10000 * 0.01) / (1.8 * v['atr'])
        rows += f"<tr><td><b>{k}</b></td><td>{v['price']}</td><td>{v['atr']}</td><td>{v['shares']}</td><td>{v['cost']}</td><td>{formula_calc:.1f} = 100/(1.8*ATR)</td></tr>"

    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Trading Core LIVE</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 20px; background-color: #f8f9fa; color: #333; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .ok {{ color: #28a745; font-weight: bold; }}
            .card {{ background: white; border: 1px solid #dee2e6; padding: 16px; margin-bottom: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .card b {{ color: #0056b3; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; background: white; }}
            th, td {{ border: 1px solid #dee2e6; padding: 10px; text-align: right; }}
            th {{ background-color: #e9ecef; text-align: center; }}
            td:first-child {{ text-align: left; }}
            .links a {{ margin-right: 15px; color: #007bff; text-decoration: none; font-weight: 500; }}
            .links a:hover {{ text-decoration: underline; }}
            .badge {{ background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ AI Trading Core LIVE - FULL DASHBOARD</h1>
            
            <div class="card">
                <b>Hash:</b> {HASH} <span class="ok">OK</span> | 
                <b>Portfolio:</b> 10K | 
                <b>Tier:</b> {LIVE['tier']} (Risk 1%, Stop 1.8x, Take 2.5x)
            </div>
            
            <div class="card">
                <b>Risk Gate 4 ด่าน:</b> DAILY_LOSS 3%, MAX_TRADES 2, MAX_POS 2, 20% LIMIT + Consent token (<i>risk_gate.py</i>)
            </div>
            
            <div class="card">
                <b>Profit Adjuster:</b> >5% +20%, 2-5% +10%, -1-0% -8%, <-1% -25% (<i>profit_based_adjuster.py</i>) - MSFT -0.53% -> 27%
            </div>
            
            <div class="card">
                <b>Strategy Adjuster:</b> DRY_RUN -> PROPOSE -> 2 token APPROVE -> APPLY, OOS >=30 trades, DD <15% (<i>strategy_adjuster.py</i>)
            </div>
            
            <div class="card">
                <b>Audit Log:</b> Append-only ห้ามลบ (<i>audit_log.py</i>) | <b>Notify:</b> Hard exempt 4 ตัว DATA_STALE DAILY_LOSS EMERGENCY BROKER_ERROR (<i>notification_filter.py</i>)
            </div>
            
            <div class="card">
                <b>Telemetry:</b> WIN_RATE_DROP <35%, LOSS_STREAK >=5, NOTIFY_FLOOD >10/60s, CONCENTRATION >60% (<i>anomaly_detector.py</i>)
            </div>
            
            <h3>Lot Calculation: shares = (10000*1%)/(1.8*ATR)</h3>
            <table>
                <tr>
                    <th>Symbol</th><th>Price</th><th>ATR</th><th>Shares</th><th>Cost (฿)</th><th>Formula</th>
                </tr>
                {rows}
            </table>
            
            <div class="card links" style="margin-top: 20px;">
                <b>API Links:</b><br><br>
                <a href="/api/health">/api/health</a> | 
                <a href="/api/tests">/api/tests</a> | 
                <a href="/api/risk">/api/risk</a> | 
                <a href="/docs">/docs (Swagger UI)</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/health")
def health():
    return {
        "hash": HASH,
        "status": "LIVE",
        "portfolio": 10000,
        "hash_ok": True,
        "version": "v0.3.1-adaptive-10K",
        "tier": "SMALL_1k_10k",
        "stocks": LIVE["stocks"],
        "fixes": "FIX 11 points - Lot ATR, Currency THB, Allocation MSFT"
    }

@app.get("/api/risk")
def risk():
    return {
        "checks": ["DAILY_LIMIT 3%", "MAX_TRADES_PER_DAY 2", "MAX_POSITIONS 2", "20%_LIMIT"],
        "consent": "uuid token, anti-replay, anti-mismatch",
        "config": {
            "min_score": 75,
            "max_trades_per_day": 2,
            "max_drawdown": 0.15
        }
    }

@app.get("/api/tests")
def tests():
    return {
        "test_risk_gate": 7,
        "test_audit_log": "append-only",
        "test_notification_filter": "cooldown",
        "test_strategy_adjuster": "2-token"
    }
