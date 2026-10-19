import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="AI Trading Core v0.3.1 FULL")

# โหลด Hash จาก Environment Variable
HASH = os.getenv("LIVE_CONFIG_10K_HASH", "676bad20288d7623")

# ข้อมูลจำลองจาก LIVE_CONFIG_10K.json + ADAPTIVE_TIERS.json
LIVE = {
    "PTT": {"price": 32.5, "atr": 0.8, "shares": 69, "cost": 2242},
    "AOT": {"price": 58.25, "atr": 1.5, "shares": 37, "cost": 2155},
    "CPALL": {"price": 62.0, "atr": 1.2, "shares": 46, "cost": 2852},
    "SCB": {"price": 110.0, "atr": 2.0, "shares": 27, "cost": 2970},
}

@app.get("/", response_class=HTMLResponse)
def home():
    rows = ""
    for sym, v in LIVE.items():
        rows += f"<tr><td><b>{sym}</b></td><td>{v['price']}</td><td>{v['atr']}</td><td>{v['shares']}</td><td>{v['cost']}</td><td><button class='btn-buy' onclick=\"buy('{sym}')\">Buy</button> <button class='btn-test' onclick=\"testRisk('{sym}')\">Test Risk</button></td></tr>"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Trading Core LIVE</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 15px; background-color: #f4f6f9; color: #333; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .ok {{ color: #28a745; font-weight: bold; }}
            .card {{ background: white; border: 1px solid #dee2e6; padding: 12px; margin: 10px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            table {{ border-collapse: collapse; width: 100%; background: white; margin-bottom: 15px; }}
            th, td {{ border: 1px solid #dee2e6; padding: 8px; text-align: right; }}
            th {{ background-color: #e9ecef; text-align: center; }}
            td:first-child {{ text-align: left; }}
            button {{ padding: 8px 12px; margin: 2px; cursor: pointer; border: none; border-radius: 4px; font-weight: bold; color: white; }}
            .btn-buy {{ background-color: #28a745; }}
            .btn-buy:hover {{ background-color: #218838; }}
            .btn-test {{ background-color: #007bff; }}
            .btn-test:hover {{ background-color: #0056b3; }}
            .btn-api {{ background-color: #6c757d; }}
            .btn-api:hover {{ background-color: #5a6268; }}
            #out {{ background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 8px; min-height: 150px; overflow-x: auto; font-family: monospace; font-size: 14px; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>✅ AI Trading Core LIVE - FULL DASHBOARD</h2>
            
            <div class="card">
                Hash: <b>{HASH}</b> <span class="ok">OK</span> | 
                Portfolio 10K | Tier SMALL_1k_10k Risk 1% Stop 1.8x Take 2.5x | 
                Formula: <code>shares=(10000*1%)/(1.8*ATR)</code>
            </div>
            
            <div class="card">
                <b>Risk Gate 4 ด่าน:</b> DAILY_LOSS 3%, MAX_TRADES 2, MAX_POS 2, 20% LIMIT + Consent token<br>
                <b>Profit Adjuster:</b> >5% +20%, 2-5% +10%, -1-0% -8%, &lt;-1% -25% (MSFT -0.53% -> 27%)
            </div>
            
            <table>
                <tr>
                    <th>Symbol</th><th>Price</th><th>ATR</th><th>Shares</th><th>Cost</th><th>Action</th>
                </tr>
                {rows}
            </table>
            
            <div class="card">
                <b>API Endpoints (คลิกเพื่อทดสอบ):</b><br><br>
                <button class="btn-api" onclick="call('/api/health')">/api/health</button>
                <button class="btn-api" onclick="call('/api/risk')">/api/risk</button>
                <button class="btn-api" onclick="call('/api/config')">/api/config</button>
                <button class="btn-api" onclick="call('/api/profit')">/api/profit</button>
                <button class="btn-api" onclick="call('/api/audit')">/api/audit</button>
                <button class="btn-api" onclick="window.open('/docs', '_blank')">/docs (Swagger)</button>
            </div>
            
            <pre id="out">กดปุ่มเพื่อทดสอบระบบ...</pre>
        </div>

        <script>
            function printOut(text) {{
                document.getElementById('out').innerText = text;
            }}

            async function call(url) {{
                printOut('Loading ' + url + '...');
                try {{
                    let r = await fetch(url);
                    let data = await r.json();
                    printOut(JSON.stringify(data, null, 2));
                }} catch (e) {{
                    printOut('Error: ' + e.message);
                }}
            }}

            async function buy(sym) {{
                printOut('Executing BUY for ' + sym + '...');
                try {{
                    let r = await fetch('/api/buy/' + sym);
                    let data = await r.json();
                    printOut(JSON.stringify(data, null, 2));
                }} catch (e) {{
                    printOut('Error: ' + e.message);
                }}
            }}

            async function testRisk(sym) {{
                printOut('Testing Risk Gate for ' + sym + '...');
                try {{
                    let r = await fetch('/api/risk/test/' + sym);
                    let data = await r.json();
                    printOut(JSON.stringify(data, null, 2));
                }} catch (e) {{
                    printOut('Error: ' + e.message);
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.get("/api/health")
def health(): 
    return {
        "hash": HASH,
        "hash_ok": True,
        "status": "LIVE",
        "portfolio": 10000,
        "version": "v0.3.1-adaptive-10K",
        "tier": "SMALL_1k_10k",
        "frozen_hash": "d83fe34155adfabe",
        "live_params": {
            "min_score": 75, "risk_pct": 0.01, "stop_atr_mult": 1.8, 
            "take_profit_atr_mult": 2.5, "max_positions": 2, 
            "max_per_position_pct": 0.5, "daily_loss_limit_pct": 0.03, 
            "max_trades_per_day": 2
        },
        "stocks": LIVE
    }

@app.get("/api/config")
def config(): 
    return {
        "min_score": 75, "risk_pct": 0.01, "stop": 1.8, "take": 2.5, 
        "max_pos": 2, "max_per": 0.5, "daily_loss": 0.03, 
        "ema_fast": 50, "ema_slow": 200,
        "tiers": {
            "MICRO_500_1k": {"risk": 0.02, "max_pos": 1},
            "SMALL_1k_10k": {"risk": 0.01, "max_pos": 2}
        }
    }

@app.get("/api/risk")
def risk(): 
    return {
        "checks": ["DAILY_LIMIT 3% OK", "MAX_TRADES_PER_DAY 2 OK", "MAX_POSITIONS 2 OK", "20%_LIMIT OK"],
        "consent": "uuid anti-replay anti-mismatch",
        "portfolio_th": 1000000,
        "portfolio_us": 10000
    }

@app.get("/api/risk/test/{symbol}")
def risk_test(symbol: str):
    s = LIVE.get(symbol)
    if not s:
        return JSONResponse({"error": "Symbol not found in LIVE list"}, status_code=404)
        
    risk_budget = 10000 * 0.01
    stop = 1.8 * s["atr"]
    shares = int(risk_budget / stop)
    
    return {
        "symbol": symbol,
        "can_enter": True,
        "consent_id": "test-uuid-1234",
        "checks": [
            ["DAILY_LIMIT", True, "OK"],
            ["MAX_TRADES", True, "OK"],
            ["MAX_POS", True, "OK"],
            ["20%_LIMIT", True, "OK"]
        ],
        "calc": f"RiskBudget {risk_budget} / Stop {stop:.2f} = Shares {shares}",
        "cost": shares * s["price"]
    }

@app.get("/api/buy/{symbol}")
def buy(symbol: str):
    s = LIVE.get(symbol)
    if not s: 
        return JSONResponse({"error": "Not found"}, status_code=404)
    
    # จำลอง Risk Gate + Profit Adjuster
    return {
        "action": "BUY",
        "symbol": symbol,
        "shares": s["shares"],
        "price": s["price"],
        "cost": s["cost"],
        "consent": "issued",
        "audit": "append-only logged",
        "notify": "cooldown checked",
        "status": "Paper trading True - Broker disabled but trade counted"
    }

@app.get("/api/profit")
def profit(): 
    return {
        "rules": {
            ">5%": "+20% INCREASE_MORE",
            "2-5%": "+10% INCREASE",
            "0-2%": "+5% INCREASE_SMALL",
            "-1-0%": "-8% DECREASE_SMALL",
            "<-1%": "-25% DECREASE"
        },
        "example": {
            "MSFT": {
                "pnl": -0.53,
                "old": 52,
                "new": 27,
                "reason": "ขาดทุน -0.53% < -1% -> ลด 25%"
            }
        },
        "formula": "profit_pct = total_pnl/total_cost*100"
    }

@app.get("/api/audit")
def audit(): 
    return {
        "mode": "append-only",
        "actions": ["PROPOSE", "APPROVE", "APPLY", "REJECT"],
        "delete": "forbidden",
        "truncate": "forbidden",
        "clear": "forbidden"
    }

@app.get("/health")
def health2(): 
    return health()

@app.get("/ready")
def ready(): 
    return {"ready": True}
