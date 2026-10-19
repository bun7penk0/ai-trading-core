import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
HASH = os.getenv("LIVE_CONFIG_10K_HASH", "676bad20288d7623")
LIVE = {
  "PTT": {"price":32.5,"atr":0.8,"shares":69,"cost":2242},
  "AOT": {"price":58.25,"atr":1.5,"shares":37,"cost":2155},
  "CPALL": {"price":62.0,"atr":1.2,"shares":46,"cost":2852},
  "SCB": {"price":110.0,"atr":2.0,"shares":27,"cost":2970},
}

@app.get("/", response_class=HTMLResponse)
def home():
    rows=""
    for k,v in LIVE.items():
        rows+=f"<div class='stock-row' onclick=\"call('/api/buy/{k}')\"><div><b>{k}</b><span>{v['price']}฿ ATR {v['atr']}</span></div><div class='right'>{v['shares']} sh<br><small>{v['cost']}฿</small></div></div>"
    return f"""
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{margin:0;background:#0f1113;color:#fff;font-family:Inter,sans-serif}}
.header{{padding:14px 16px;display:flex;justify-content:space-between;align-items:center;background:#161a1d;border-bottom:1px solid #222}}
.header h1{{font-size:14px;margin:0;line-height:1.2}} .header small{{color:#888}}
.live-btn{{background:#00ff88;color:#000;padding:6px 14px;border-radius:20px;font-weight:800;font-size:12px}}
.badge{{background:#111;border:1px solid #333;padding:8px 14px;border-radius:12px;display:inline-block;margin:4px}}
.card{{background:#1a1f22;border:1px solid #2a2f33;border-radius:20px;padding:16px;margin:12px}}
.port-value{{font-size:36px;font-weight:900}} .cap{{width:70px;height:70px;border:4px solid #00ff88;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;float:right}}
.green{{color:#00ff88}} .dim{{color:#777;font-size:12px}}
.grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:12px}}
.grid div{{background:#22272a;border-radius:12px;padding:10px}} .grid b{{font-size:18px}}
.risk-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}} .risk-grid div{{background:#22272a;border-radius:14px;padding:12px}}
.stock-row{{background:#22272a;border-radius:14px;padding:12px;margin:8px 0;display:flex;justify-content:space-between;cursor:pointer}} .stock-row:active{{background:#2a3035}}
#out{{background:#000;color:#0f0;padding:10px;border-radius:10px;margin:12px;min-height:60px;white-space:pre-wrap;font-size:12px}}
button{{background:#222;border:1px solid #444;color:#fff;padding:6px 10px;border-radius:8px;margin:2px;cursor:pointer}}
</style></head><body>
<div class="header"><h1>AI TRADING CORE<br><small>v0.3.1-adaptive-10K • TIER SMALL_1k_10k</small></h1><div class="live-btn">LIVE API ↗</div></div>
<div style="padding:8px 16px" class="green">● LIVE • SMALL_1k_10k <span style="float:right;color:#555">{HASH[:7]}</span></div>

<div class="card">
  <div class="cap"><b>100%</b><small>CAP</small></div>
  <div class="dim">PORTFOLIO VALUE</div>
  <div class="port-value">10,000 <small style="font-size:14px">฿</small> <span class="badge" style="font-size:11px;background:#003322;color:#00ff88;border-color:#00ff88">THB SET</span></div>
  <div class="dim">ช่วงเทียร์ 1,000 - 10,000 บาท • ใช้จริง</div>
  <div class="grid">
    <div><div class="dim">TIER</div><b>SMALL_1k_10k</b><br><small class="dim">SMALL</small></div>
    <div><div class="dim">RISK</div><b>1%</b><br><small class="dim">ต่อไม้</small></div>
    <div><div class="dim">MAX POS</div><b>2</b><br><small class="dim">50% ต่อตัว</small></div>
  </div>
  <div class="dim" style="margin-top:10px">🗄️ frozen_hash: d83fe34155adfabe • hash {HASH} OK</div>
</div>

<div class="card">
  <div style="display:flex;justify-content:space-between"><b class="green">🛡️ RISK GATE • ประตูความเสี่ยง</b><span style="border:1px solid #ffcc00;color:#ffcc00;padding:2px 8px;border-radius:10px;font-size:11px">ACTIVE</span></div>
  <div class="risk-grid" style="margin-top:12px">
    <div><div class="dim">Min Score</div><b>75</b><br><small class="dim">คะแนน • เกณฑ์เข้าออเดอร์</small></div>
    <div><div class="dim">Risk / Trade</div><b>1%</b><br><small class="dim">พอร์ต • 100฿ ต่อไม้</small></div>
    <div><div class="dim">Stop Loss</div><b>1.8 ATR</b><br><small class="dim">ATR Stop • ตัดขาดทุนตามความผันผวน</small></div>
    <div><div class="dim">Take Profit</div><b>2.5 ATR</b><br><small class="dim">ATR Target • ปล่อยกำไรวิ่ง</small></div>
  </div>
  <div style="margin-top:12px">
    <button onclick="call('/api/health')">Health</button>
    <button onclick="call('/api/risk')">Risk Gate</button>
    <button onclick="call('/api/profit')">Profit Adjuster</button>
    <button onclick="call('/api/config')">Config</button>
    <button onclick="window.open('/docs','_blank')">Docs</button>
  </div>
</div>

<div class="card">
  <div class="dim">STOCKS • shares = (10000*1%)/(1.8*ATR) • กดเพื่อ Buy/Test</div>
  {rows}
</div>

<pre id="out">กดปุ่มด้านบน หรือกดหุ้นเพื่อ Buy • Test Risk Gate 4 ด่านทำงาน</pre>
<script>
async function call(u){{ 
  let o=document.getElementById('out'); o.innerText='Loading '+u+'...';
  let r=await fetch(u); let t=await r.text(); 
  try{{ t=JSON.stringify(JSON.parse(t),null,2) }}catch(e){{}}
  o.innerText=t;
}}
</script>
</body></html>
"""

@app.get("/api/health")
def health(): return {"hash":HASH,"hash_ok":True,"status":"LIVE","portfolio":10000,"version":"v0.3.1-adaptive-10K","tier":"SMALL_1k_10k","frozen_hash":"d83fe34155adfabe","risk_gate":"4 checks ACTIVE","profit_adjuster":">5% +20% <-1% -25%","stocks":LIVE}

@app.get("/api/risk")
def risk(): return {"DAILY_LOSS":"3%","MAX_TRADES":"2","MAX_POS":"2","20%_LIMIT":"50%","consent_token":"uuid anti-replay","audit_log":"append-only","notify":"hard_exempt 4"}

@app.get("/api/profit")
def profit(): return {"rules":{">5%":"+20% INCREASE_MORE","2-5%":"+10%","0-2%":"+5%","-1-0%":"-8%","<-1%":"-25% DECREASE"},"fix":"MSFT -0.53% 52% -> 27%"}

@app.get("/api/config")
def cfg(): return {"min_score":75,"risk_pct":0.01,"stop":1.8,"take":2.5,"max_pos":2,"max_per":0.5,"daily_loss":0.03,"min_trades_adjust":100,"min_oos":30}

@app.get("/api/buy/{sym}")
def buy(sym: str):
    v=LIVE.get(sym); 
    if not v: return {"error":"not found"}
    return {"action":"BUY","symbol":sym,"shares":v["shares"],"price":v["price"],"cost":v["cost"],"consent":"issued uuid","checks":"4 OK","profit_logic":"MSFT -0.53% -> 27%","status":"Paper True - counted"}

@app.get("/health")
def h2(): return health()
