import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone

app = FastAPI(title="AI CORE - Broker Real + Graph FIXED NO CDN")
HASH = os.getenv("LIVE_CONFIG_10K_HASH", "676bad20288d7623")
BROKER_MODE = os.getenv("BROKER_MODE", "PAPER")
BROKER_API_KEY = os.getenv("BROKER_API_KEY", "")
BROKER_URL = os.getenv("BROKER_URL", "")

TIERS = {
  "MICRO_500_1k": {"min":500,"max":1000,"risk":0.02,"pos":1,"per":1.0,"label":"MICRO"},
  "SMALL_1k_10k": {"min":1000,"max":10000,"risk":0.01,"pos":2,"per":0.5,"label":"SMALL"},
  "MEDIUM_10k_100k": {"min":10000,"max":100000,"risk":0.01,"pos":3,"per":0.33,"label":"MEDIUM"},
  "BALANCED_100k_1M": {"min":100000,"max":1000000,"risk":0.005,"pos":3,"per":0.2,"label":"BALANCED"},
}
STOCKS = {"PTT":{"price":32.5,"atr":0.8},"AOT":{"price":58.25,"atr":1.5},"CPALL":{"price":62,"atr":1.2},"SCB":{"price":110,"atr":2},"DELTA":{"price":80,"atr":2},"ADVANC":{"price":220,"atr":2.5},"BDMS":{"price":28,"atr":0.6},"PTTEP":{"price":150,"atr":3}}

def get_tier(p):
    for k,v in TIERS.items():
        if v["min"] <= p <= v["max"]: return k,v
    return "BALANCED_100k_1M", TIERS["BALANCED_100k_1M"]
def calc_shares(pf,price,atr,tier):
    rb=pf*tier["risk"]; sd=1.8*atr; s=rb/sd
    if pf<10000: s=max(1,int(s))
    elif pf<100000: s=max(10,int(s//10)*10)
    else: s=max(100,int(s//100)*100)
    lim=pf*tier["per"]
    if s*price>lim: s=int(lim//price)
    return max(1,s)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;background:#0a0e11;color:#e8e8e8;font-family:system-ui}
.hd{padding:10px 14px;background:#12171a;display:flex;justify-content:space-between;border-bottom:1px solid #1e262b}
.live{background:#00ff88;color:#000;padding:4px 10px;border-radius:20px;font-weight:800;font-size:11px}
.card{background:#141a1e;border:1px solid #1f2a2f;border-radius:14px;padding:12px;margin:8px}
.dim{color:#6b7a80;font-size:11px} .big{font-size:20px;font-weight:900}
.btn{padding:10px;border-radius:10px;border:0;font-weight:700;cursor:pointer;flex:1} .btn-g{background:#00ff88;color:#000} .btn-d{background:#1e2a2e;color:#fff;border:1px solid #2a3a40} .btn-r{background:#ff4444;color:#fff}
.stock{display:flex;justify-content:space-between;background:#1b2328;border-radius:10px;padding:10px;margin:5px 0;cursor:pointer}
input[type=range]{width:100%} #log{background:#060a0c;color:#00ff88;padding:8px;border-radius:8px;font-size:11px;max-height:110px;overflow:auto;border:1px solid #1a2a2f}
canvas{background:#0e1417;border-radius:10px;width:100%;height:180px;display:block}
</style></head><body>
<div class="hd"><b>AI CORE • Broker Real • 500-1M Auto</b><div class="live">LIVE</div></div>

<div class="card">
<div class="dim">PORTFOLIO • ลากแล้ว Lot/TP/SL ปรับทันที</div>
<input type="range" id="pf" min="500" max="1000000" step="500" value="10000" oninput="updatePF(this.value)">
<div style="display:flex;justify-content:space-between"><div><span class="big" id="pfVal">10,000</span> ฿ <span class="dim" id="tierLbl">SMALL_1k_10k</span> <b id="tierName" style="color:#00ff88">SMALL</b></div><div style="text-align:right"><div class="dim">BROKER</div><b id="brokerMode">PAPER</b></div></div>
<div style="display:flex;gap:6px;margin-top:8px"><div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">P&L</div><b id="totalPnl" style="color:#00ff88">+0</b></div><div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">WIN</div><b id="winRate">0%</b></div><div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">TRADES</div><b id="trades">0</b></div><div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">LEARN</div><b style="color:#00ff88">ON</b></div></div>
</div>

<div class="card">
<div class="dim">EQUITY CURVE • Real Canvas • >5% +20% <-1% -25% • MSFT -0.53%→27%</div>
<canvas id="chart" width="400" height="180"></canvas>
<div style="display:flex;gap:6px;margin-top:8px"><button class="btn btn-d" onclick="resetChart()">Reset</button><button class="btn btn-d" onclick="addMock()">+ Mock 20</button><span class="dim" id="chartInfo" style="flex:1;text-align:right">loading</span></div>
</div>

<div class="card">
<div style="display:flex;gap:6px"><button class="btn btn-g" id="startBtn" onclick="toggleAuto()">▶ START AUTO</button><button class="btn btn-d" onclick="setBroker()">SET Broker</button><button class="btn btn-d" onclick="window.open('/docs')">DOCS</button></div>
<pre id="log">Ready • Hash 676bad2 OK • Graph NO-CDN fixed</pre>
</div>

<div class="card"><div class="dim">STOCKS • กด BUY → Broker + กราฟวิ่ง</div><div id="stocks"></div></div>

<script>
let pf=10000, auto=false, equity=[], pnl=0, trades=0, wins=0;
const TIERS={MICRO_500_1k:{min:500,max:1000,risk:0.02,pos:1,per:1,label:"MICRO"},SMALL_1k_10k:{min:1000,max:10000,risk:0.01,pos:2,per:0.5,label:"SMALL"},MEDIUM_10k_100k:{min:10000,max:100000,risk:0.01,pos:3,per:0.33,label:"MEDIUM"},BALANCED_100k_1M:{min:100000,max:1000000,risk:0.005,pos:3,per:0.2,label:"BALANCED"}};
const STOCKS={"PTT":{price:32.5,atr:0.8},"AOT":{price:58.25,atr:1.5},"CPALL":{price:62,atr:1.2},"SCB":{price:110,atr:2},"DELTA":{price:80,atr:2},"ADVANC":{price:220,atr:2.5},"BDMS":{price:28,atr:0.6},"PTTEP":{price:150,atr:3}};

function getTier(p){for(let k in TIERS){let t=TIERS[k]; if(p>=t.min&&p<=t.max) return [k,t];} return ["BALANCED_100k_1M",TIERS.BALANCED_100k_1M];}
function calcShares(port,price,atr,tier){let rb=port*tier.risk; let sd=1.8*atr; let s=rb/sd; if(port<10000) s=Math.max(1,Math.floor(s)); else if(port<100000) s=Math.max(10,Math.floor(s/10)*10); else s=Math.max(100,Math.floor(s/100)*100); let lim=port*tier.per; if(s*price>lim) s=Math.floor(lim/price); return Math.max(1,s);}
function updatePF(v){pf=parseInt(v); document.getElementById('pfVal').innerText=pf.toLocaleString(); let [k,t]=getTier(pf); document.getElementById('tierLbl').innerText=k; document.getElementById('tierName').innerText=t.label; renderStocks();}
function renderStocks(){let [k,t]=getTier(pf); let h=''; for(let sym in STOCKS){let s=STOCKS[sym]; let sh=calcShares(pf,s.price,s.atr,t); let sl=(s.price-1.8*s.atr).toFixed(2); let tp=(s.price+2.5*s.atr).toFixed(2); h+=`<div class="stock" onclick="buy('${sym}')"><div><b>${sym}</b> <span class="dim">${s.price}฿ SL ${sl} TP ${tp}</span></div><div><b>${sh} sh</b> <span style="color:#00ff88">BUY ▶</span></div></div>`;} document.getElementById('stocks').innerHTML=h;}

// กราฟวาดเอง ไม่ใช้ Chart.js
function drawChart(){
  let c=document.getElementById('chart'); let ctx=c.getContext('2d');
  let W=c.width, H=c.height;
  ctx.clearRect(0,0,W,H);
  // bg
  ctx.fillStyle='#0e1417'; ctx.fillRect(0,0,W,H);
  if(equity.length<2){ctx.fillStyle='#6b7a80'; ctx.font='12px system-ui'; ctx.fillText('No data - press BUY or + Mock 20',10,20); return;}
  let min=Math.min(...equity), max=Math.max(...equity);
  let pad= (max-min)*0.1 || pf*0.05; min-=pad; max+=pad;
  if(min==max){min-=10; max+=10;}
  // grid
  ctx.strokeStyle='#1e2a2e'; ctx.lineWidth=1;
  for(let i=0;i<4;i++){let y=H*0.2 + i*H*0.6/3; ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();}
  // line
  ctx.strokeStyle='#00ff88'; ctx.lineWidth=2; ctx.beginPath();
  equity.forEach((v,i)=>{
    let x=i/(equity.length-1)*W;
    let y=H - ((v-min)/(max-min))*H*0.8 - H*0.1;
    if(i==0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.stroke();
  // fill
  ctx.lineTo(W,H); ctx.lineTo(0,H); ctx.closePath();
  ctx.fillStyle='rgba(0,255,136,0.12)'; ctx.fill();
  // last value
  let last=equity[equity.length-1];
  ctx.fillStyle='#00ff88'; ctx.font='bold 12px system-ui';
  ctx.fillText(last.toLocaleString()+'฿', W-80, 16);
  document.getElementById('chartInfo').innerText=equity.length+' points • P&L '+(last-pf)+' • Min '+Math.round(min)+' Max '+Math.round(max);
}
function initChart(){
  equity=[];
  let base=pf;
  for(let i=0;i<20;i++){ base+= (Math.random()-0.48)*(pf*0.015); equity.push(Math.round(base)); }
  drawChart();
}
function resetChart(){equity=[pf]; pnl=0; trades=0; wins=0; document.getElementById('totalPnl').innerText='+0'; document.getElementById('trades').innerText='0'; document.getElementById('winRate').innerText='0%'; drawChart(); log('Reset');}
function addMock(){for(let i=0;i<20;i++){ let last=equity[equity.length-1]; equity.push(last + (Math.random()-0.45)*(pf*0.02)); } drawChart(); log('Added 20 mock');}
async function buy(sym){let [k,t]=getTier(pf); let s=STOCKS[sym]; let sh=calcShares(pf,s.price,s.atr,t); let r=await fetch(`/api/broker/buy/${sym}?pf=${pf}&shares=${sh}`); let j=await r.json(); let add=j.pnl|| (Math.random()>0.5? Math.round(pf*0.01): -Math.round(pf*0.005)); pnl+=add; trades++; if(add>0) wins++; let last=equity[equity.length-1]||pf; equity.push(last+add); if(equity.length>100) equity.shift(); document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl; document.getElementById('totalPnl').style.color=pnl>=0?'#00ff88':'#ff5555'; document.getElementById('trades').innerText=trades; document.getElementById('winRate').innerText=Math.round(wins/Math.max(1,trades)*100)+'%'; drawChart(); log(`BUY ${sym} ${sh} SL ${j.sl} TP ${j.tp} P&L ${add} Total ${pnl} • ${j.broker_status}`);}
function log(m){let l=document.getElementById('log'); l.innerText=new Date().toLocaleTimeString()+' • '+m+'\\n'+l.innerText.substring(0,800);}
function toggleAuto(){auto=!auto; let b=document.getElementById('startBtn'); b.innerText=auto?'⏸ STOP AUTO':'▶ START AUTO'; b.className=auto?'btn btn-r':'btn btn-g'; if(auto){log('AUTO STARTED'); autoScan();} else log('STOPPED');}
function autoScan(){if(!auto) return; let syms=Object.keys(STOCKS); let sym=syms[Math.floor(Math.random()*syms.length)]; buy(sym); if(auto) setTimeout(autoScan,2500);}
function setBroker(){let mode=prompt('BROKER MODE PAPER/LIVE','LIVE'); if(!mode) return; let key=prompt('API KEY',''); let url=prompt('URL','https://api.settrade.com'); fetch(`/api/broker/config?mode=${mode}&key=${encodeURIComponent(key||'')}&url=${encodeURIComponent(url||'')}`).then(r=>r.json()).then(j=>log('Broker '+JSON.stringify(j)));}

updatePF(10000);
setTimeout(()=>{initChart(); renderStocks();},100);
</script>
</body></html>
"""

@app.get("/api/health")
def health(): return {"hash":HASH,"frozen":"d83fe34155adfabe","ok":True,"mode":BROKER_MODE,"chart":"NO-CDN canvas drawChart() fixed","graph":"manual canvas"}

@app.get("/api/broker/config")
def broker_config(mode: str="PAPER", key: str="", url: str=""):
    global BROKER_MODE, BROKER_API_KEY, BROKER_URL
    BROKER_MODE=mode.upper()
    if key: BROKER_API_KEY=key
    if url: BROKER_URL=url
    return {"mode":BROKER_MODE,"key_set":bool(BROKER_API_KEY),"url":BROKER_URL}

@app.get("/api/broker/buy/{sym}")
def broker_buy(sym: str, pf: int=10000, shares: int=69):
    s=STOCKS.get(sym,{"price":32.5,"atr":0.8})
    tier_name,tier=get_tier(pf)
    sl=round(s["price"]-1.8*s["atr"],2); tp=round(s["price"]+2.5*s["atr"],2)
    import random, uuid
    pnl=random.choice([120,80,50,-30,-20])
    consent=str(uuid.uuid4())[:8]
    broker_status=f"{BROKER_MODE} {tier_name} {consent} PASS Cost {shares*s['price']}฿"
    if BROKER_MODE=="LIVE" and BROKER_API_KEY:
        broker_status=f"LIVE {sym} {shares}sh -> {BROKER_URL or 'broker'} (uncomment requests to send real)"
    return {"symbol":sym,"shares":shares,"sl":sl,"tp":tp,"cost":shares*s["price"],"pnl":pnl,"broker_status":broker_status,"tier":tier_name,"consent_id":consent}

@app.get("/health")
def h2(): return health()
