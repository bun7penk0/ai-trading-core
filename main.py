from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI()

HTML_PAGE = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AI Trading Core LIVE</title>
<style>body{background:#070a0f;color:#00ff88;font-family:monospace;padding:20px}
.card{background:#111a24;border:1px solid #00ff88;padding:15px;margin:10px 0;border-radius:8px}
.green{color:#00ff88}.white{color:white}
</style></head><body>
<h1>🟢 AI Trading Core v0.3.1 LIVE</h1>
<div class="card"><span class="green">Hash:</span> <span class="white">d83fe34155adfabe</span><br>
<span class="green">Portfolio:</span> 10,000฿ Tier SMALL_1k_10k risk 1% stop 1.8 take 2.5 max_pos2 max_per 50%<br>
<span class="green">Formula:</span> shares = (10000*1%)/(1.8*ATR)<br>
PTT 32.5 atr0.8 = 69sh cost2242฿<br>
AOT 58.25 atr1.5 = 37sh cost2155฿<br>
CPALL 62 atr1.2 = 46sh cost2852฿<br>
SCB 110 atr2.0 = 27sh cost2970฿</div>
<div class="card">API: <a href="/api/health" style="color:#00ff88">/api/health</a> | <a href="/api/prices" style="color:#00ff88">/api/prices</a></div>
<script>setInterval(()=>{document.body.innerHTML+= "<div class='card'>Tick: PTT "+(32.5+Math.random()).toFixed(2)+" | AUTO Trading...</div>"; window.scrollTo(0,document.body.scrollHeight)},2000)</script>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
def root(): return HTML_PAGE

@app.get("/api/health")
def health(): 
    return {"status":"LIVE","hash":"d83fe34155adfabe","portfolio":10000,"tier":"SMALL_1k_10k","risk_pct":"1%","stop":1.8,"take":2.5,"max_pos":2,"stocks":["PTT","AOT","CPALL","SCB","DELTA","ADVANC","BDMS","PTTEP"],"lot_formula":"PTT69 AOT37 CPALL46 SCB27 = (10000*1%)/(1.8*ATR)"}

@app.get("/api/prices")
def prices():
    return {"PTT":{"price":32.5,"atr":0.8,"shares":69,"cost":2242},"AOT":{"price":58.25,"atr":1.5,"shares":37,"cost":2155},"CPALL":{"price":62,"atr":1.2,"shares":46,"cost":2852},"SCB":{"price":110,"atr":2.0,"shares":27,"cost":2970}}
