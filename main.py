# main.py - FINAL FIXED - PERSISTENT LOCALSTORAGE - NO RESET ON EXIT
# frozen d83fe34155adfabe - แก้รีเซ็ตเมื่อออกจากแอพ
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI CORE - PERSISTENT FIX")
HASH = "676bad20288d7623"
FROZEN = "d83fe34155adfabe"
BROKER_MODE = "PAPER"
MODE = "DEMO"

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
.badge-demo{background:#ffb400;color:#000}.badge-paper{background:#00ff88;color:#000}.badge-fix{background:#6ae; color:#000}
.card{background:#141a1e;border:1px solid #1f2a2f;border-radius:14px;padding:12px;margin:8px}
.dim{color:#6b7a80;font-size:11px}.big{font-size:22px;font-weight:900}
.btn{padding:10px;border-radius:10px;border:0;font-weight:700;cursor:pointer;flex:1}
.btn-g{background:#00ff88;color:#000}.btn-d{background:#1e2a2e;color:#fff;border:1px solid #2a3a40}.btn-r{background:#ff4444;color:#fff}.btn-s{background:#ffb400;color:#000}.btn-save{background:#6ae;color:#000}
.stock{display:flex;justify-content:space-between;background:#1b2328;border-radius:10px;padding:10px;margin:6px 0}
.pos{background:#12261c;border:1px solid #1a4a2a;border-radius:10px;padding:8px;margin:4px 0;display:flex;justify-content:space-between}
#log{background:#060a0c;color:#00ff88;padding:8px;border-radius:8px;font-size:11px;max-height:180px;overflow:auto;border:1px solid #1a2a2f}
canvas{background:#0e1417;border-radius:10px;width:100%;height:200px;display:block}
</style></head><body>
<div class="hd"><div><b>AI CORE • Persistent FIX</b> <span class="dim">ไม่รีเซ็ตแล้ว • MICRO 500฿</span></div><div><span class="badge badge-demo">DEMO</span> <span class="badge badge-paper">PAPER</span> <span class="badge badge-fix">FIXED</span></div></div>
<div class="card">
<div class="dim">✅ FIX: ออกจากแอพแล้วไม่รีเซ็ต • localStorage ถาวร • frozen d83fe34</div>
<input type="range" id="pf" min="500" max="10000" step="500" value="500" oninput="updatePF(this.value)">
<div style="display:flex;justify-content:space-between"><div><span class="big" id="pfVal">500</span> ฿ <span class="dim" id="tierLbl">MICRO_500_1k</span> <b id="tierName" style="color:#00ff88">MICRO</b></div><div style="text-align:right"><div class="dim">MODE</div><b>DEMO-PAPER</b> • <span id="posCount">0 pos</span> • <span id="saveStatus" class="dim" style="color:#6ae">💾 Auto-Save</span></div></div>
<div style="display:flex;gap:6px;margin-top:8px">
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">P&L สุทธิ</div><b id="totalPnl" style="color:#00ff88">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">WIN</div><b id="winRate">0%</b><div class="dim">เป้า 55%</div></div>
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">TRADES</div><b id="trades">0</b></div>
<div style="flex:1;background:#1b2328;border-radius:8px;padding:6px;text-align:center"><div class="dim">Avg/ไม้</div><b id="avgTrade">0฿</b></div>
</div>
</div>
<div class="card"><div class="dim">EQUITY CURVE • Persistent ไม่หาย</div><canvas id="chart" width="400" height="200"></canvas><div style="display:flex;gap:6px;margin-top:8px"><button class="btn btn-save" onclick="manualSave()">💾 SAVE NOW</button><button class="btn btn-d" onclick="resetChart()">Reset</button><button class="btn btn-d" onclick="closeAll()">Close All</button><span class="dim" id="chartInfo" style="flex:1;text-align:right"></span></div></div>
<div class="card"><div class="dim">POSITIONS • TP 2.5 ATR SL 1.8 ATR</div><div id="positions"><div class="dim">ยังไม่มี - กด BUY</div></div></div>
<div class="card"><div style="display:flex;gap:6px"><button class="btn btn-g" id="startBtn" onclick="toggleAuto()">▶ START AUTO (PERSISTENT)</button><button class="btn btn-d" onclick="location.href='/health'">/health</button><button class="btn btn-d" onclick="location.href='/docs'">/docs</button></div><pre id="log">Ready • Persistent FIX • localStorage enabled • ออกจากแอพแล้วไม่รีเซ็ตแล้ว</pre></div>
<div class="card"><div class="dim">STOCKS • PTT AOT CPALL SCB DELTA ADVANC BDMS PTTEP</div><div id="stocks"></div></div>
<script>
let pf=500,auto=false,equity=[500],pnl=0,trades=0,wins=0,positions={};
const TIERS={MICRO_500_1k:{min:500,max:1000,risk:0.02,pos:1,per:1,fee:0.0015,label:"MICRO"},SMALL_1k_10k:{min:1000,max:10000,risk:0.01,pos:2,per:0.5,fee:0.0015,label:"SMALL"}};
const STOCKS={"PTT":{price:32.5,atr:0.8},"AOT":{price:58.25,atr:1.5},"CPALL":{price:62,atr:1.2},"SCB":{price:110,atr:2},"DELTA":{price:80,atr:2},"ADVANC":{price:220,atr:2.5},"BDMS":{price:28,atr:0.6},"PTTEP":{price:150,atr:3}};
const STORAGE_KEY='ai_core_persistent_v1';
function saveState(){try{let data={pf,pnl,trades,wins,equity,positions,log:document.getElementById('log').innerText,ts:Date.now()};localStorage.setItem(STORAGE_KEY,JSON.stringify(data));document.getElementById('saveStatus').innerText='💾 Saved '+new Date().toLocaleTimeString();setTimeout(()=>{document.getElementById('saveStatus').innerText='💾 Auto-Save';},2000);}catch(e){}}
function loadState(){try{let raw=localStorage.getItem(STORAGE_KEY);if(!raw) return null;let d=JSON.parse(raw);pf=d.pf||500;pnl=d.pnl||0;trades=d.trades||0;wins=d.wins||0;equity=d.equity||[pf];positions=d.positions||{};document.getElementById('pf').value=pf;document.getElementById('pfVal').innerText=pf.toLocaleString();let [k,t]=getTier(pf);document.getElementById('tierLbl').innerText=k;document.getElementById('tierName').innerText=t.label;if(d.log)document.getElementById('log').innerText=d.log+'\\n'+new Date().toLocaleTimeString()+' • RESTORED P&L '+pnl.toFixed(2)+'฿';document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';document.getElementById('trades').innerText=trades;document.getElementById('winRate').innerText=(trades?Math.round(wins/trades*100):0)+'%';document.getElementById('avgTrade').innerText=(trades?(pnl/trades).toFixed(2):'0')+'฿';return true;}catch(e){return null;}}
function manualSave(){saveState();log('MANUAL SAVE สำเร็จ • ออกจากแอพแล้วไม่หายแล้ว');}
function getTier(p){for(let k in TIERS){let t=TIERS[k];if(p>=t.min&&p<=t.max) return [k,t];}return ["SMALL_1k_10k",TIERS.SMALL_1k_10k];}
function calcShares(port,price,atr,tier){let rb=port*tier.risk;let sd=1.8*atr;let s=rb/sd;if(port<10000) s=Math.max(1,Math.floor(s));else s=Math.max(10,Math.floor(s/10)*10);let lim=port*tier.per;if(s*price>lim) s=Math.floor(lim/price);return Math.max(1,s);}
function updatePF(v){if(Object.keys(positions).length>0){alert('มี pos อยู่ Close All ก่อน');document.getElementById('pf').value=pf;return;}pf=parseInt(v);document.getElementById('pfVal').innerText=pf.toLocaleString();let [k,t]=getTier(pf);document.getElementById('tierLbl').innerText=k;document.getElementById('tierName').innerText=t.label;equity=[pf];pnl=0;trades=0;wins=0;positions={};drawChart();renderPositions();renderStocks();saveState();log('เปลี่ยนพอร์ตเป็น '+pf+' ฿ Tier '+k);}
function renderStocks(){let [k,t]=getTier(pf);let h='';for(let sym in STOCKS){let s=STOCKS[sym];let sh=calcShares(pf,s.price,s.atr,t);let sl=(s.price-1.8*s.atr).toFixed(2);let tp=(s.price+2.5*s.atr).toFixed(2);let held=positions[sym]?positions[sym].shares+'sh':'';h+=`<div class="stock"><div><b>${sym}</b> <span class="dim">${s.price}฿ SL ${sl} TP ${tp} ${held}</span></div><div style="display:flex;gap:4px"><button class="btn btn-g" style="padding:6px 10px" onclick="buy('${sym}')">BUY ${sh}</button><button class="btn btn-s" style="padding:6px 10px" onclick="sell('${sym}')">SELL</button></div></div>`;}document.getElementById('stocks').innerHTML=h;}
function renderPositions(){let count=Object.keys(positions).length;document.getElementById('posCount').innerText=count+' pos';if(count==0){document.getElementById('positions').innerHTML='<div class="dim">ยังไม่มี - กด BUY • ออกจากแอพแล้วกลับมา pos ยังอยู่</div>';return;}let html='';for(let sym in positions){let p=positions[sym];let cur=STOCKS[sym].price;let unreal=(cur-p.entry)*p.shares;html+=`<div class="pos"><div><b>${sym}</b> ${p.shares}sh @${p.entry.toFixed(2)} → ${cur.toFixed(2)} ${(unreal>=0?'+':'')+unreal.toFixed(2)}฿<br><span class="dim">SL ${p.sl.toFixed(2)} TP ${p.tp.toFixed(2)}</span></div><div><button class="btn btn-s" onclick="sell('${sym}')">SELL</button></div></div>`;}document.getElementById('positions').innerHTML=html;}
function drawChart(){let c=document.getElementById('chart');let ctx=c.getContext('2d');let W=c.width,H=c.height;ctx.clearRect(0,0,W,H);ctx.fillStyle='#0e1417';ctx.fillRect(0,0,W,H);if(equity.length<2){ctx.fillStyle='#6b7a80';ctx.font='12px system-ui';ctx.fillText('BUY to start - Persistent ไม่หายเมื่อออกจากแอพ',10,20);return;}let min=Math.min(...equity),max=Math.max(...equity);let pad=(max-min)*0.2||pf*0.02;min-=pad;max+=pad;if(min==max){min-=5;max+=5;}ctx.strokeStyle='#1e2a2e';for(let i=0;i<3;i++){let y=H*0.15+i*H*0.7/2;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}ctx.strokeStyle='#00ff88';ctx.lineWidth=2;ctx.beginPath();equity.forEach((v,i)=>{let x=i/(equity.length-1)*W;let y=H-((v-min)/(max-min))*H*0.7-H*0.15;if(i==0) ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fillStyle='rgba(0,255,136,0.12)';ctx.fill();document.getElementById('chartInfo').innerText=equity.length+' pts • '+min.toFixed(0)+'→'+max.toFixed(0)+' • P&L '+(equity[equity.length-1]-pf).toFixed(2)+'฿';}
function resetChart(){if(!confirm('Reset ลบข้อมูลถาวร?')) return;equity=[pf];pnl=0;trades=0;wins=0;positions={};document.getElementById('totalPnl').innerText='+0';document.getElementById('pnlPct').innerText='0%';document.getElementById('trades').innerText='0';document.getElementById('winRate').innerText='0%';document.getElementById('avgTrade').innerText='0฿';localStorage.removeItem(STORAGE_KEY);drawChart();renderPositions();renderStocks();log('Reset • ลบ localStorage แล้ว');}
function closeAll(){for(let sym in positions) sell(sym,'CLOSE ALL');}
async function buy(sym){let [k,t]=getTier(pf);if(Object.keys(positions).length>=t.pos && !positions[sym]){log('MAX POS '+t.pos+' ต้อง SELL ก่อน');return;}let s=STOCKS[sym];let sh=calcShares(pf,s.price,s.atr,t);let r=await fetch('/api/broker/buy/'+sym+'?pf='+pf+'&shares='+sh);let j=await r.json();positions[sym]={shares:sh,entry:s.price,sl:parseFloat(j.sl),tp:parseFloat(j.tp)};renderPositions();renderStocks();drawChart();saveState();log('BUY '+sym+' '+sh+' @'+s.price+' SL '+j.sl+' TP '+j.tp+' • Saved');}
async function sell(sym,reason){if(!positions[sym]){log('No pos '+sym);return;}let pos=positions[sym];let entry=pos.entry;let isWin=Math.random()>0.45;let exitPrice=isWin?entry+(Math.random()*0.8+0.2)*(pos.tp-entry):entry-(Math.random()*0.8+0.2)*(entry-pos.sl);exitPrice=Math.max(pos.sl*0.99,Math.min(pos.tp*1.01,exitPrice));let gross=(exitPrice-entry)*pos.shares;let fee=(entry*pos.shares+exitPrice*pos.shares)*0.0015;let slip=(entry*pos.shares)*0.001;let net=gross-fee-slip;await fetch('/api/broker/sell/'+sym+'?pf='+pf+'&shares='+pos.shares+'&pnl='+net.toFixed(2));pnl+=net;trades++;if(net>0)wins++;equity.push(equity[equity.length-1]+net);if(equity.length>150)equity.shift();document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';document.getElementById('trades').innerText=trades;document.getElementById('winRate').innerText=Math.round(wins/Math.max(1,trades)*100)+'%';document.getElementById('avgTrade').innerText=(trades?(pnl/trades).toFixed(2):'0')+'฿';delete positions[sym];renderPositions();renderStocks();drawChart();saveState();log('SELL '+sym+' @'+exitPrice.toFixed(2)+' Net '+(net>=0?'+':'')+net.toFixed(2)+' Total '+pnl.toFixed(2)+' '+(isWin?'WIN':'LOSS')+' Saved');}
function log(m){let l=document.getElementById('log');l.innerText=new Date().toLocaleTimeString()+' • '+m+'\\n'+l.innerText.substring(0,2000);}
async function toggleAuto(){auto=!auto;let b=document.getElementById('startBtn');b.innerText=auto?'⏸ STOP AUTO':'▶ START AUTO (PERSISTENT)';b.className=auto?'btn btn-r':'btn btn-g';if(auto){log('AUTO STARTED PERSISTENT • Auto-Save ทุกไม้');while(auto){if(Object.keys(positions).length>0 && Math.random()>0.55){let held=Object.keys(positions);await sell(held[Math.floor(Math.random()*held.length)],'AUTO');}else{let syms=Object.keys(STOCKS);let sym=syms[Math.floor(Math.random()*syms.length)];if(!positions[sym]) await buy(sym);}renderPositions();await new Promise(r=>setTimeout(r,1800+Math.random()*1500));}}else log('STOPPED • Saved');}
let restored=loadState();if(restored){drawChart();renderPositions();renderStocks();}else{updatePF(500);setTimeout(()=>{renderStocks();drawChart();},100);}
setInterval(()=>{if(Object.keys(positions).length>0||trades>0) saveState();},5000);
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML_PAGE, headers={"Cache-Control": "no-store"})
@app.get("/health")
def health():
    return {"ok":True,"fixed":"PERSISTENT localStorage - no reset","storage":"ai_core_persistent_v1","frozen":"d83fe34155adfabe"}
@app.get("/api/broker/buy/{sym}")
def broker_buy(sym: str, pf: int = 500, shares: int = 1):
    s = STOCKS.get(sym, {"price":32.5,"atr":0.8})
    sl = round(s["price"]-1.8*s["atr"],2)
    tp = round(s["price"]+2.5*s["atr"],2)
    return {"sl": sl, "tp": tp}
@app.get("/api/broker/sell/{sym}")
def broker_sell(sym: str, pf: int = 500, shares: int = 1, pnl: float = 0):
    return {"pnl": pnl}
