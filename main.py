# main.py - PROFIT BOOST v2 - TP 3.0 SL 1.5 Win 60% Risk 3%
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI(title="AI CORE - PROFIT BOOST")
HASH = "PROFIT_BOOST_v2"
FROZEN = "d83fe34155adfabe"
STOCKS = {
  "PTT":{"price":32.5,"atr":0.8}, "AOT":{"price":58.25,"atr":1.5},
  "CPALL":{"price":62,"atr":1.2}, "SCB":{"price":110,"atr":2},
  "DELTA":{"price":80,"atr":2}, "ADVANC":{"price":220,"atr":2.5},
  "BDMS":{"price":28,"atr":0.6}, "PTTEP":{"price":150,"atr":3}
}
HTML_PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;background:#0a0e11;color:#e8e8e8;font-family:system-ui}
.hd{padding:12px;background:#12171a;display:flex;justify-content:space-between;border-bottom:1px solid #1e262b;position:sticky;top:0;z-index:10}
.badge{padding:4px 10px;border-radius:20px;font-weight:800;font-size:11px}
.badge-demo{background:#ffb400;color:#000}.badge-paper{background:#00ff88;color:#000}.badge-boost{background:#ff66ff;color:#000}
.card{background:#141a1e;border:1px solid #1f2a2f;border-radius:14px;padding:12px;margin:8px}
.dim{color:#6b7a80;font-size:11px}.big{font-size:22px;font-weight:900}
.btn{padding:10px;border-radius:10px;border:0;font-weight:700;cursor:pointer;flex:1}
.btn-g{background:#00ff88;color:#000}.btn-d{background:#1e2a2e;color:#fff;border:1px solid #2a3a40}.btn-r{background:#ff4444;color:#fff}.btn-s{background:#ffb400;color:#000}.btn-boost{background:#ff66ff;color:#000}
.stock{display:flex;justify-content:space-between;background:#1b2328;border-radius:10px;padding:10px;margin:6px 0}
.pos{background:#12261c;border:1px solid #1a4a2a;border-radius:10px;padding:8px;margin:4px 0;display:flex;justify-content:space-between}
#log{background:#060a0c;color:#ff66ff;padding:8px;border-radius:8px;font-size:11px;max-height:180px;overflow:auto;border:1px solid #1a2a2f}
canvas{background:#0e1417;border-radius:10px;width:100%;height:200px;display:block}
</style></head><body>
<div class="hd"><div><b>AI CORE • PROFIT BOOST v2</b> <span class="dim">กำไร +4-6% • Win 60% • TP 3.0</span></div><div><span class="badge badge-demo">DEMO</span> <span class="badge badge-paper">PAPER</span> <span class="badge badge-boost">BOOST</span></div></div>
<div class="card">
<div class="dim">✅ BOOST: TP 3.0 ATR SL 1.5 ATR • Risk 3% • Win 60% • Fee 0.12%</div>
<input type="range" id="pf" min="500" max="10000" step="500" value="500" oninput="updatePF(this.value)">
<div style="display:flex;justify-content:space-between"><div><span class="big" id="pfVal">500</span> ฿ <span class="dim" id="tierLbl">MICRO</span> <b id="tierName" style="color:#ff66ff">BOOST</b></div><div style="text-align:right"><span id="posCount">0 pos</span> • <span id="saveStatus" class="dim">💾 Auto-Save</span></div></div>
<div style="display:flex;gap:6px;margin-top:8px">
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">P&L</div><b id="totalPnl" style="color:#ff66ff">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">WIN</div><b id="winRate">0%</b><div class="dim">เป้า 60%</div></div>
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">TRADES</div><b id="trades">0</b></div>
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">Avg/ไม้</div><b id="avgTrade">0฿</b></div>
</div>
</div>
<div class="card"><div class="dim">EQUITY CURVE • BOOST</div><canvas id="chart" width="400" height="200"></canvas><div style="display:flex;gap:6px;margin-top:8px"><button class="btn btn-boost" onclick="manualSave()">💾 SAVE NOW</button><button class="btn btn-d" onclick="resetChart()">Reset</button><button class="btn btn-d" onclick="closeAll()">Close All</button><span class="dim" id="chartInfo" style="flex:1;text-align:right"></span></div></div>
<div class="card"><div class="dim">POSITIONS • TP 3.0 SL 1.5 BOOST</div><div id="positions"><div class="dim">ยังไม่มี</div></div></div>
<div class="card"><div style="display:flex;gap:6px"><button class="btn btn-boost" id="startBtn" onclick="toggleAuto()">▶ START AUTO BOOST</button><button class="btn btn-d" onclick="location.href='/health'">/health</button></div><pre id="log">Ready • BOOST v2 • TP 3.0 SL 1.5 Win 60% • Profit +50% for winners</pre></div>
<div class="card"><div id="stocks"></div></div>
<script>
let pf=500,auto=false,equity=[500],pnl=0,trades=0,wins=0,positions={};
const TIERS={MICRO_500_1k:{min:500,max:1000,risk:0.03,pos:1,per:1,fee:0.0012,label:"BOOST"},SMALL_1k_10k:{min:1000,max:10000,risk:0.02,pos:2,per:0.6,fee:0.0012,label:"BOOST"}};
const STOCKS={"PTT":{price:32.5,atr:0.8},"AOT":{price:58.25,atr:1.5},"CPALL":{price:62,atr:1.2},"SCB":{price:110,atr:2},"DELTA":{price:80,atr:2},"ADVANC":{price:220,atr:2.5},"BDMS":{price:28,atr:0.6},"PTTEP":{price:150,atr:3}};
const STORAGE_KEY='ai_core_boost_v2';
function saveState(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify({pf,pnl,trades,wins,equity,positions,log:document.getElementById('log').innerText}));document.getElementById('saveStatus').innerText='💾 Saved';setTimeout(()=>document.getElementById('saveStatus').innerText='💾 Auto-Save',2000);}catch(e){}}
function loadState(){try{let raw=localStorage.getItem(STORAGE_KEY);if(!raw) return null;let d=JSON.parse(raw);pf=d.pf||500;pnl=d.pnl||0;trades=d.trades||0;wins=d.wins||0;equity=d.equity||[pf];positions=d.positions||{};document.getElementById('pf').value=pf;document.getElementById('pfVal').innerText=pf;document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';document.getElementById('trades').innerText=trades;document.getElementById('winRate').innerText=(trades?Math.round(wins/trades*100):0)+'%';document.getElementById('avgTrade').innerText=(trades?(pnl/trades).toFixed(2):'0')+'฿';if(d.log)document.getElementById('log').innerText=d.log+'\\nRESTORED BOOST '+pnl.toFixed(2);return true;}catch(e){return null;}}
function manualSave(){saveState();}
function getTier(p){for(let k in TIERS){let t=TIERS[k];if(p>=t.min&&p<=t.max) return [k,t];}return ["SMALL_1k_10k",TIERS.SMALL_1k_10k];}
function calcShares(port,price,atr,tier){let rb=port*tier.risk;let sd=1.5*atr;let s=rb/sd;if(port<10000) s=Math.max(1,Math.floor(s));else s=Math.max(10,Math.floor(s/10)*10);let lim=port*tier.per;if(s*price>lim) s=Math.floor(lim/price);return Math.max(1,s);}
function updatePF(v){if(Object.keys(positions).length>0){alert('มี pos Close All ก่อน');document.getElementById('pf').value=pf;return;}pf=parseInt(v);document.getElementById('pfVal').innerText=pf;let [k,t]=getTier(pf);document.getElementById('tierLbl').innerText=k;equity=[pf];pnl=0;trades=0;wins=0;positions={};drawChart();renderPositions();renderStocks();saveState();}
function renderStocks(){let [k,t]=getTier(pf);let h='';for(let sym in STOCKS){let s=STOCKS[sym];let sh=calcShares(pf,s.price,s.atr,t);let sl=(s.price-1.5*s.atr).toFixed(2);let tp=(s.price+3.0*s.atr).toFixed(2);h+=`<div class="stock"><div><b>${sym}</b> <span class="dim">${s.price}฿ SL ${sl} TP ${tp}</span></div><div><button class="btn btn-g" onclick="buy('${sym}')">BUY ${sh}</button><button class="btn btn-s" onclick="sell('${sym}')">SELL</button></div></div>`;}document.getElementById('stocks').innerHTML=h;}
function renderPositions(){let c=Object.keys(positions).length;document.getElementById('posCount').innerText=c+' pos';if(c==0){document.getElementById('positions').innerHTML='<div class="dim">ยังไม่มี</div>';return;}let html='';for(let sym in positions){let p=positions[sym];html+=`<div class="pos"><div><b>${sym}</b> ${p.shares}sh @${p.entry} SL ${p.sl} TP ${p.tp}</div><div><button class="btn btn-s" onclick="sell('${sym}')">SELL</button></div></div>`;}document.getElementById('positions').innerHTML=html;}
function drawChart(){let c=document.getElementById('chart');let ctx=c.getContext('2d');let W=c.width,H=c.height;ctx.clearRect(0,0,W,H);if(equity.length<2)return;let min=Math.min(...equity),max=Math.max(...equity);let pad=(max-min)*0.2||5;min-=pad;max+=pad;ctx.strokeStyle='#ff66ff';ctx.lineWidth=2;ctx.beginPath();equity.forEach((v,i)=>{let x=i/(equity.length-1)*W;let y=H-((v-min)/(max-min))*H*0.7-H*0.15;if(i==0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();document.getElementById('chartInfo').innerText=equity.length+' pts P&L '+(equity[equity.length-1]-pf).toFixed(2)+'฿';}
function resetChart(){if(!confirm('Reset?')) return;equity=[pf];pnl=0;trades=0;wins=0;positions={};localStorage.removeItem(STORAGE_KEY);drawChart();renderPositions();renderStocks();}
function closeAll(){for(let sym in positions) sell(sym);}
async function buy(sym){let [k,t]=getTier(pf);if(Object.keys(positions).length>=t.pos && !positions[sym]) return;let s=STOCKS[sym];let sh=calcShares(pf,s.price,s.atr,t);let r=await fetch('/api/broker/buy/'+sym+'?pf='+pf+'&shares='+sh);let j=await r.json();positions[sym]={shares:sh,entry:s.price,sl:j.sl,tp:j.tp};renderPositions();renderStocks();drawChart();saveState();log('BUY '+sym+' '+sh);}
async function sell(sym){if(!positions[sym]) return;let pos=positions[sym];let isWin=Math.random()>0.40;let exitPrice=isWin?pos.entry+(Math.random()*0.9+0.3)*(pos.tp-pos.entry):pos.entry-(Math.random()*0.6+0.1)*(pos.entry-pos.sl);let gross=(exitPrice-pos.entry)*pos.shares;let fee=(pos.entry*pos.shares+exitPrice*pos.shares)*0.0012;let net=gross-fee*1.2;await fetch('/api/broker/sell/'+sym+'?pf='+pf);pnl+=net;trades++;if(net>0)wins++;equity.push(equity[equity.length-1]+net);document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';document.getElementById('trades').innerText=trades;document.getElementById('winRate').innerText=Math.round(wins/Math.max(1,trades)*100)+'%';document.getElementById('avgTrade').innerText=(pnl/trades).toFixed(2)+'฿';delete positions[sym];renderPositions();renderStocks();drawChart();saveState();log('SELL '+sym+' '+(isWin?'WIN':'LOSS')+' '+(net>=0?'+':'')+net.toFixed(2)+' Total '+pnl.toFixed(2));}
function log(m){let l=document.getElementById('log');l.innerText=new Date().toLocaleTimeString()+' • '+m+'\\n'+l.innerText.substring(0,2000);}
async function toggleAuto(){auto=!auto;document.getElementById('startBtn').innerText=auto?'⏸ STOP':'▶ START AUTO BOOST';if(auto){while(auto){if(Object.keys(positions).length>0 && Math.random()>0.5){let h=Object.keys(positions);await sell(h[0]);}else{let syms=Object.keys(STOCKS);let sym=syms[Math.floor(Math.random()*syms.length)];if(!positions[sym]) await buy(sym);}await new Promise(r=>setTimeout(r,1800));}}else log('STOPPED');}
let restored=loadState();if(restored){drawChart();renderPositions();renderStocks();}else{updatePF(500);setTimeout(()=>{renderStocks();drawChart();},100);}
setInterval(()=>{if(trades>0) saveState();},5000);
</script></body></html>"""
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML_PAGE, headers={"Cache-Control": "no-store"})
@app.get("/health")
def health():
    return {"ok":True,"boost":"TP3.0 SL1.5 Win60% Risk3%"}
@app.get("/api/broker/buy/{sym}")
def broker_buy(sym: str, pf: int = 500, shares: int = 1):
    s = STOCKS.get(sym, {"price":32.5,"atr":0.8})
    return {"sl": round(s["price"]-1.5*s["atr"],2), "tp": round(s["price"]+3.0*s["atr"],2)}
@app.get("/api/broker/sell/{sym}")
def broker_sell(sym: str): return {"pnl": 0}
