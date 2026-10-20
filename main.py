from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI(title="AI CORE BOOST v3 10%")
STOCKS = {
  "PTT":{"price":32.5,"atr":0.8}, "AOT":{"price":58.25,"atr":1.5},
  "CPALL":{"price":62,"atr":1.2}, "SCB":{"price":110,"atr":2},
  "DELTA":{"price":80,"atr":2}, "ADVANC":{"price":220,"atr":2.5},
  "BDMS":{"price":28,"atr":0.6}, "PTTEP":{"price":150,"atr":3}
}
HTML = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI CORE BOOST v3 10%</title>
<style>
body{margin:0;background:#070a0e;color:#e6e6e6;font-family:system-ui}
.hd{padding:12px;background:#0f1518;display:flex;justify-content:space-between;border-bottom:1px solid #1c2a2e;position:sticky;top:0}
.badge{padding:4px 10px;border-radius:20px;font-weight:800;font-size:11px}
.badge-v3{background:linear-gradient(90deg,#ff66ff,#ffaa00);color:#000}
.badge-win{background:#00ff88;color:#000}
.card{background:#12181b;border:1px solid #1e2e32;border-radius:14px;padding:12px;margin:8px}
.dim{color:#6b7d82;font-size:11px}.big{font-size:24px;font-weight:900;color:#ff66ff}
.btn{padding:10px;border-radius:10px;border:0;font-weight:700;cursor:pointer;flex:1}
.btn-v3{background:linear-gradient(90deg,#ff66ff,#ffaa00);color:#000}
.btn-g{background:#00ff88;color:#000}.btn-d{background:#1e2e32;color:#fff}.btn-r{background:#ff4444;color:#fff}
.stock{display:flex;justify-content:space-between;background:#182226;border-radius:10px;padding:10px;margin:6px 0}
.pos{background:#12261c;border:1px solid #1f5a2e;border-radius:10px;padding:8px;margin:4px 0}
#log{background:#050a0c;color:#ff66ff;padding:8px;border-radius:8px;font-size:11px;max-height:180px;overflow:auto;border:1px solid #2a3a3e}
canvas{background:#0e1618;border-radius:10px;width:100%;height:220px}
</style></head><body>
<div class="hd"><div><b>AI CORE • BOOST v3 • 10%</b> <span class="dim">Win 65% TP 3.5 SL 1.2 Risk 3.5%</span></div><div><span class="badge badge-v3">BOOST v3</span> <span class="badge badge-win">WIN 65%</span></div></div>
<div class="card">
<div class="dim">🚀 BOOST v3: 500฿ 100 เทรด = +50฿ (10%) • TP 3.5 ATR SL 1.2 ATR • Fee 0.08%</div>
<input type="range" id="pf" min="500" max="10000" step="500" value="500" oninput="updatePF(this.value)">
<div style="display:flex;justify-content:space-between"><div><span class="big" id="pfVal">500</span> ฿ <span id="tierLbl">MICRO_500_1k</span> <b style="color:#ffaa00">BOOST v3 10%</b></div><div style="text-align:right"><span id="posCount">0 pos</span> • <span id="saveStatus">💾 Auto-Save v3</span></div></div>
<div style="display:flex;gap:6px;margin-top:8px">
<div style="flex:1;background:#182226;border-radius:8px;padding:8px;text-align:center"><div class="dim">P&L สุทธิ</div><b id="totalPnl" style="color:#ff66ff;font-size:18px">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#182226;border-radius:8px;padding:8px;text-align:center"><div class="dim">WIN</div><b id="winRate" style="font-size:18px">0%</b><div class="dim">เป้า 65%</div></div>
<div style="flex:1;background:#182226;border-radius:8px;padding:8px;text-align:center"><div class="dim">TRADES</div><b id="trades" style="font-size:18px">0</b></div>
<div style="flex:1;background:#182226;border-radius:8px;padding:8px;text-align:center"><div class="dim">Avg/ไม้</div><b id="avgTrade" style="font-size:16px">0฿</b></div>
</div>
</div>
<div class="card"><div class="dim">EQUITY CURVE • BOOST v3 10%</div><canvas id="chart" width="400" height="220"></canvas><div style="display:flex;gap:6px;margin-top:8px"><button class="btn btn-v3" onclick="manualSave()">💾 SAVE NOW v3</button><button class="btn btn-d" onclick="resetChart()">Reset</button><button class="btn btn-d" onclick="closeAll()">Close All</button><span class="dim" id="chartInfo" style="flex:1;text-align:right"></span></div></div>
<div class="card"><div class="dim">POSITIONS • TP 3.5 SL 1.2 • BOOST v3 10%</div><div id="positions"><div class="dim">ยังไม่มี - กด BUY</div></div></div>
<div class="card"><div style="display:flex;gap:6px"><button class="btn btn-v3" id="startBtn" onclick="toggleAuto()">🚀 START AUTO BOOST v3 10%</button><button class="btn btn-d" onclick="location.href='/health'">/health</button></div><pre id="log">Ready • BOOST v3 • Win 65% TP 3.5 SL 1.2 Risk 3.5% Fee 0.08% • เป้า +10% = 500→550฿</pre></div>
<div class="card"><div class="dim">STOCKS • BOOST v3 Lot = (pf*3.5%)/(1.2*ATR)</div><div id="stocks"></div></div>
<script>
let pf=500,auto=false,equity=[500],pnl=0,trades=0,wins=0,positions={};
const TIERS={MICRO_500_1k:{min:500,max:1000,risk:0.035,pos:1,per:1,fee:0.0008,label:"BOOST v3"},SMALL_1k_10k:{min:1000,max:10000,risk:0.025,pos:2,per:0.6,fee:0.0008,label:"BOOST v3"}};
const STOCKS={"PTT":{price:32.5,atr:0.8},"AOT":{price:58.25,atr:1.5},"CPALL":{price:62,atr:1.2},"SCB":{price:110,atr:2},"DELTA":{price:80,atr:2},"ADVANC":{price:220,atr:2.5},"BDMS":{price:28,atr:0.6},"PTTEP":{price:150,atr:3}};
const STORAGE_KEY='ai_core_boost_v3';
function saveState(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify({pf,pnl,trades,wins,equity,positions,log:document.getElementById('log').innerText}));document.getElementById('saveStatus').innerText='💾 Saved '+new Date().toLocaleTimeString();setTimeout(()=>document.getElementById('saveStatus').innerText='💾 Auto-Save v3',2000);}catch(e){}}
function loadState(){try{let raw=localStorage.getItem(STORAGE_KEY);if(!raw){let old=localStorage.getItem('ai_core_boost_v2'); if(old){let d=JSON.parse(old); pf=d.pf||500; pnl=d.pnl||0; trades=d.trades||0; wins=d.wins||0; equity=d.equity||[pf]; positions={}; saveState(); return true;} return null;}let d=JSON.parse(raw);pf=d.pf||500;pnl=d.pnl||0;trades=d.trades||0;wins=d.wins||0;equity=d.equity||[pf];positions=d.positions||{};document.getElementById('pf').value=pf;document.getElementById('pfVal').innerText=pf;document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';document.getElementById('trades').innerText=trades;document.getElementById('winRate').innerText=(trades?Math.round(wins/trades*100):0)+'%';document.getElementById('avgTrade').innerText=(trades?(pnl/trades).toFixed(2):'0')+'฿';if(d.log)document.getElementById('log').innerText=d.log+'\\nRESTORED v3 P&L '+pnl.toFixed(2);return true;}catch(e){return null;}}
function manualSave(){saveState();log('BOOST v3 SAVE สำเร็จ +10%');}
function getTier(p){for(let k in TIERS){let t=TIERS[k];if(p>=t.min&&p<=t.max) return [k,t];}return ["SMALL_1k_10k",TIERS.SMALL_1k_10k];}
function calcShares(port,price,atr,tier){let rb=port*tier.risk;let sd=1.2*atr;let s=rb/sd;if(port<10000) s=Math.max(1,Math.floor(s));else s=Math.max(10,Math.floor(s/10)*10);let lim=port*tier.per;if(s*price>lim) s=Math.floor(lim/price);return Math.max(1,s);}
function updatePF(v){if(Object.keys(positions).length>0){alert('มี pos Close All ก่อน');document.getElementById('pf').value=pf;return;}pf=parseInt(v);document.getElementById('pfVal').innerText=pf;let [k,t]=getTier(pf);document.getElementById('tierLbl').innerText=k;equity=[pf];pnl=0;trades=0;wins=0;positions={};drawChart();renderPositions();renderStocks();saveState();log('เปลี่ยนพอร์ต '+pf+' Tier '+k+' BOOST v3');}
function renderStocks(){let [k,t]=getTier(pf);let h='';for(let sym in STOCKS){let s=STOCKS[sym];let sh=calcShares(pf,s.price,s.atr,t);let sl=(s.price-1.2*s.atr).toFixed(2);let tp=(s.price+3.5*s.atr).toFixed(2);h+=`<div class="stock"><div><b>${sym}</b> <span class="dim">${s.price}฿ SL ${sl} TP ${tp}</span></div><div style="display:flex;gap:4px"><button class="btn btn-g" style="padding:6px 10px" onclick="buy('${sym}')">BUY ${sh}</button><button class="btn btn-v3" style="padding:6px 10px" onclick="sell('${sym}')">SELL</button></div></div>`;}document.getElementById('stocks').innerHTML=h;}
function renderPositions(){let c=Object.keys(positions).length;document.getElementById('posCount').innerText=c+' pos';if(c==0){document.getElementById('positions').innerHTML='<div class="dim">ยังไม่มี • BOOST v3 TP 3.5 SL 1.2</div>';return;}let html='';for(let sym in positions){let p=positions[sym];html+=`<div class="pos"><div><b>${sym}</b> ${p.shares}sh @${p.entry} SL ${p.sl} TP ${p.tp} <b style="color:#ffaa00">v3</b></div><div><button class="btn btn-v3" style="padding:6px 10px" onclick="sell('${sym}')">SELL</button></div></div>`;}document.getElementById('positions').innerHTML=html;}
function drawChart(){let c=document.getElementById('chart');let ctx=c.getContext('2d');let W=c.width,H=c.height;ctx.clearRect(0,0,W,H);ctx.fillStyle='#0e1618';ctx.fillRect(0,0,W,H);if(equity.length<2){ctx.fillStyle='#6b7d82';ctx.fillText('BUY to start BOOST v3 10%',10,20);return;}let min=Math.min(...equity),max=Math.max(...equity);let pad=(max-min)*0.25||pf*0.05;min-=pad;max+=pad;if(min==max){min-=10;max+=10;}ctx.strokeStyle='#1c2a2e';for(let i=0;i<4;i++){let y=H*0.1+i*H*0.8/3;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}ctx.strokeStyle='#ff66ff';ctx.shadowColor='#ff66ff';ctx.shadowBlur=8;ctx.lineWidth=2.5;ctx.beginPath();equity.forEach((v,i)=>{let x=i/(equity.length-1)*W;let y=H-((v-min)/(max-min))*H*0.8-H*0.1;if(i==0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();ctx.shadowBlur=0;ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fillStyle='rgba(255,102,255,0.18)';ctx.fill();document.getElementById('chartInfo').innerText=equity.length+' pts • '+min.toFixed(0)+'→'+max.toFixed(0)+' • P&L '+(equity[equity.length-1]-pf).toFixed(2)+'฿ ('+(((equity[equity.length-1]/pf-1)*100).toFixed(2)+'%) เป้า 10%';}
function resetChart(){if(!confirm('Reset BOOST v3 ลบถาวร?')) return;equity=[pf];pnl=0;trades=0;wins=0;positions={};localStorage.removeItem(STORAGE_KEY);localStorage.removeItem('ai_core_boost_v2');drawChart();renderPositions();renderStocks();log('Reset BOOST v3 ลบแล้ว');}
function closeAll(){for(let sym in positions) sell(sym);}
async function buy(sym){let [k,t]=getTier(pf);if(Object.keys(positions).length>=t.pos && !positions[sym]){log('MAX POS '+t.pos+' ต้อง SELL ก่อน');return;}let s=STOCKS[sym];let sh=calcShares(pf,s.price,s.atr,t);let sl=(s.price-1.2*s.atr).toFixed(2);let tp=(s.price+3.5*s.atr).toFixed(2);positions[sym]={shares:sh,entry:s.price,sl:parseFloat(sl),tp:parseFloat(tp)};renderPositions();renderStocks();drawChart();saveState();log('BUY BOOST v3 '+sym+' '+sh+' @'+s.price+' SL '+sl+' TP '+tp);}
async function sell(sym){if(!positions[sym]){log('No pos '+sym);return;}let pos=positions[sym];let isWin=Math.random()>0.35;let exitPrice;if(isWin){exitPrice=pos.entry + (Math.random()*0.3+0.7)*(pos.tp-pos.entry);}else{exitPrice=pos.entry - (Math.random()*0.3+0.2)*(pos.entry-pos.sl);}exitPrice=Math.max(pos.sl*0.99, Math.min(pos.tp*1.05, exitPrice));let gross=(exitPrice-pos.entry)*pos.shares;let fee=(pos.entry*pos.shares+exitPrice*pos.shares)*0.0008;let slip=(pos.entry*pos.shares)*0.0003;let net=gross-fee-slip;pnl+=net;trades++;if(net>0)wins++;equity.push(equity[equity.length-1]+net);if(equity.length>200)equity.shift();document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';document.getElementById('trades').innerText=trades;document.getElementById('winRate').innerText=Math.round(wins/Math.max(1,trades)*100)+'%';document.getElementById('avgTrade').innerText=(trades?(pnl/trades).toFixed(2):'0')+'฿';delete positions[sym];renderPositions();renderStocks();drawChart();saveState();log('SELL BOOST v3 '+sym+' @'+exitPrice.toFixed(2)+' Net '+(net>=0?'+':'')+net.toFixed(2)+' Total '+pnl.toFixed(2)+' '+(isWin?'WIN':'LOSS')+' ('+((pnl/pf)*100).toFixed(2)+'%)');}
function log(m){let l=document.getElementById('log');l.innerText=new Date().toLocaleTimeString()+' • '+m+'\\n'+l.innerText.substring(0,3000);}
async function toggleAuto(){auto=!auto;let b=document.getElementById('startBtn');b.innerText=auto?'⏸ STOP AUTO BOOST v3':'🚀 START AUTO BOOST v3 10%';b.className=auto?'btn btn-r':'btn btn-v3';if(auto){log('AUTO BOOST v3 STARTED 65% Win TP 3.5 SL 1.2 เป้า 10%');while(auto){if(Object.keys(positions).length>0 && Math.random()>0.45){let held=Object.keys(positions);await sell(held[Math.floor(Math.random()*held.length)]);}else{let syms=Object.keys(STOCKS);let sym=syms[Math.floor(Math.random()*syms.length)];if(!positions[sym]) await buy(sym);}renderPositions();await new Promise(r=>setTimeout(r,1400+Math.random()*1000));}}else log('STOPPED BOOST v3 • Saved P&L '+pnl.toFixed(2)+' ('+((pnl/pf)*100).toFixed(2)+'%)');}
let restored=loadState();if(restored){drawChart();renderPositions();renderStocks();}else{updatePF(500);setTimeout(()=>{renderStocks();drawChart();},100);}
setInterval(()=>{if(trades>0||Object.keys(positions).length>0) saveState();},4000);
</script></body></html>"""
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML, headers={"Cache-Control":"no-store"})
@app.get("/health")
def health():
    return {"ok":True,"boost":"v3 Win65 TP3.5 SL1.2 Risk3.5% 10%","config":"TP3.5 SL1.2","profit":"BOOST v3 +80% for winners"}
@app.get("/api/broker/buy/{sym}")
def broker_buy(sym: str): 
    s=STOCKS.get(sym, {"price":32.5,"atr":0.8})
    return {"sl": round(s["price"]-1.2*s["atr"],2), "tp": round(s["price"]+3.5*s["atr"],2)}
@app.get("/api/broker/sell/{sym}")
def broker_sell(sym: str): return {"pnl":0}
