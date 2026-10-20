from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI()

HTML_PAGE = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI CORE BOOST v3 FINAL STATIC</title>
<style>
body{margin:0;background:#070a0e;color:#e6e6e6;font-family:system-ui}
.hd{padding:12px;background:#0f1518;border-bottom:2px solid #ff66ff;position:sticky;top:0;z-index:99}
.card{background:#12181b;border:1px solid #2a3a3e;border-radius:14px;padding:14px;margin:10px}
.dim{color:#7a8a8e;font-size:12px}
.big{font-size:26px;font-weight:900;color:#ff66ff}
.btn{padding:14px;border-radius:12px;border:0;font-weight:900;cursor:pointer;font-size:14px;margin:3px}
.btn-v3{background:#ff66ff;color:#000;width:100%}
.btn-g{background:#00ff88;color:#000}
.btn-d{background:#1e2e32;color:#fff}
.btn-r{background:#ff4444;color:#fff}
.stock{display:flex;justify-content:space-between;align-items:center;background:#182226;border-radius:10px;padding:14px;margin:8px 0;border:1px solid #2a3a3e}
#log{background:#000;color:#00ff88;padding:12px;border-radius:8px;font-size:12px;height:180px;overflow:auto;border:1px solid #333;white-space:pre-wrap}
canvas{background:#0e1618;border-radius:10px;width:100%;height:200px;display:block}
input[type=range]{width:100%;margin:10px 0}
</style>
</head>
<body>
<div class="hd"><b>AI CORE • BOOST v3 STATIC ✅</b><br><span class="dim">PORT + SAVE + กดติด 100% - หุ้นอยู่ใน HTML เลย</span></div>

<div class="card">
<div class="dim">เลือกพอร์ต (PORT) - ลากได้ 500฿ ถึง 10,000฿</div>
<input type="range" id="pfRange" min="500" max="10000" step="500" value="500">
<div style="display:flex;justify-content:space-between">
<div><span class="big" id="pfVal">500</span> ฿ <span id="tierLbl" style="color:#ffaa00">MICRO_500_1k</span></div>
<div><span id="posCount">0 pos</span><br><span id="saveStatus" style="color:#00ff88;font-size:11px">Ready</span></div>
</div>
<div style="display:flex;gap:8px;margin-top:10px">
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">P&L</div><b id="totalPnl" style="color:#ff66ff;font-size:20px">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">WIN</div><b id="winRate" style="font-size:20px">0%</b></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">TRADES</div><b id="trades" style="font-size:20px">0</b></div>
</div>
</div>

<div class="card"><canvas id="chart" width="400" height="200"></canvas></div>
<div class="card"><div class="dim">POSITIONS</div><div id="positions">ยังไม่มี</div></div>

<div class="card">
<button class="btn btn-v3" id="startBtn">🚀 START AUTO BOOST v3 10%</button>
<div style="display:flex;gap:6px;margin-top:8px">
<button class="btn btn-d" onclick="buy('PTT')">TEST BUY PTT</button>
<button class="btn btn-d" onclick="closeAll()">Close All</button>
<button class="btn btn-r" onclick="hardReset()">RESET</button>
</div>
<pre id="log">Ready - กดได้เลย
</pre>
</div>

<div class="card">
<b>STOCKS - กด BUY ได้เลย (8 ตัว) - STATIC HTML กดติด 100%</b>
<div id="stocks">
<div class="stock"><div><b>PTT</b><br><span class="dim">32.5฿ SL 31.54 TP 35.30</span></div><div><button class="btn btn-g" onclick="buy('PTT')">BUY</button></div></div>
<div class="stock"><div><b>AOT</b><br><span class="dim">58.25฿ SL 56.45 TP 63.50</span></div><div><button class="btn btn-g" onclick="buy('AOT')">BUY</button></div></div>
<div class="stock"><div><b>CPALL</b><br><span class="dim">62฿ SL 60.56 TP 66.20</span></div><div><button class="btn btn-g" onclick="buy('CPALL')">BUY</button></div></div>
<div class="stock"><div><b>SCB</b><br><span class="dim">110฿ SL 107.60 TP 117.00</span></div><div><button class="btn btn-g" onclick="buy('SCB')">BUY</button></div></div>
<div class="stock"><div><b>DELTA</b><br><span class="dim">80฿ SL 77.60 TP 87.00</span></div><div><button class="btn btn-g" onclick="buy('DELTA')">BUY</button></div></div>
<div class="stock"><div><b>ADVANC</b><br><span class="dim">220฿ SL 217.00 TP 228.75</span></div><div><button class="btn btn-g" onclick="buy('ADVANC')">BUY</button></div></div>
<div class="stock"><div><b>BDMS</b><br><span class="dim">28฿ SL 27.28 TP 30.10</span></div><div><button class="btn btn-g" onclick="buy('BDMS')">BUY</button></div></div>
<div class="stock"><div><b>PTTEP</b><br><span class="dim">150฿ SL 146.40 TP 160.50</span></div><div><button class="btn btn-g" onclick="buy('PTTEP')">BUY</button></div></div>
</div>
</div>

<script>
var pf = 500, auto = false, equity = [500], pnl = 0, trades = 0, wins = 0, positions = {};
var prices = {"PTT":32.5,"AOT":58.25,"CPALL":62,"SCB":110,"DELTA":80,"ADVANC":220,"BDMS":28,"PTTEP":150};
var atrs = {"PTT":0.8,"AOT":1.5,"CPALL":1.2,"SCB":2,"DELTA":2,"ADVANC":2.5,"BDMS":0.6,"PTTEP":3};

function $(id){return document.getElementById(id);}
function logMsg(m){var el=$('log');var t=new Date().toLocaleTimeString();el.textContent=t+' '+m+'\n'+el.textContent;}
function getTier(p){return p<=1000?"MICRO_500_1k":"SMALL_1k_10k";}
function calcShares(price, atr){var risk=pf*(pf<=1000?0.035:0.025);var s=Math.floor(risk/(1.2*atr));if(s<1)s=1;if(s>25)s=25;return s;}

function saveState(){try{localStorage.setItem('ai_core_final_static', JSON.stringify({pf:pf,pnl:pnl,trades:trades,wins:wins,equity:equity,positions:positions}));$('saveStatus').textContent='💾 Saved '+new Date().toLocaleTimeString();}catch(e){}}
function loadState(){try{var raw=localStorage.getItem('ai_core_final_static');if(!raw)return false;var d=JSON.parse(raw);pf=d.pf||500;pnl=d.pnl||0;trades=d.trades||0;wins=d.wins||0;equity=d.equity||[pf];positions=d.positions||{}; $('pfRange').value=pf;$('pfVal').textContent=pf;$('tierLbl').textContent=getTier(pf);$('totalPnl').textContent=(pnl>=0?'+':'')+pnl.toFixed(2);$('pnlPct').textContent=((pnl/pf)*100).toFixed(2)+'%';$('trades').textContent=trades;$('winRate').textContent=(trades?Math.round(wins/trades*100):0)+'%';logMsg('RESTORED P&L '+pnl.toFixed(2));return true;}catch(e){return false;}}

function renderPositions(){
  var el=$('positions');var keys=Object.keys(positions);$('posCount').textContent=keys.length+' pos';
  if(keys.length===0){el.textContent='ยังไม่มี - กด BUY ได้เลย';return;}
  el.innerHTML='';keys.forEach(function(sym){var p=positions[sym];var row=document.createElement('div');row.style.cssText='display:flex;justify-content:space-between;background:#12261c;padding:10px;margin:4px 0;border-radius:8px';row.innerHTML='<span><b>'+sym+'</b> '+p.shares+'sh @'+p.entry+'</span>';var b=document.createElement('button');b.className='btn btn-d';b.textContent='SELL';b.onclick=function(){sell(sym);};row.appendChild(b);el.appendChild(row);});
}
function drawChart(){var c=$('chart'),ctx=c.getContext('2d'),W=c.width,H=c.height;ctx.clearRect(0,0,W,H);ctx.fillStyle='#0e1618';ctx.fillRect(0,0,W,H);if(equity.length<2){ctx.fillStyle='#666';ctx.fillText('กด START',10,20);return;}var min=Math.min.apply(null,equity),max=Math.max.apply(null,equity),pad=Math.max((max-min)*0.2,5);min-=pad;max+=pad;ctx.strokeStyle='#ff66ff';ctx.lineWidth=3;ctx.beginPath();for(var i=0;i<equity.length;i++){var x=i/(equity.length-1)*W,y=H-((equity[i]-min)/(max-min))*H*0.8-H*0.1;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}ctx.stroke();}

function changePortfolio(v){if(Object.keys(positions).length>0){alert('มี Position อยู่ Close All ก่อน');$('pfRange').value=pf;return;}pf=parseInt(v);$('pfVal').textContent=pf;$('tierLbl').textContent=getTier(pf);equity=[pf];pnl=0;trades=0;wins=0;positions={};$('totalPnl').textContent='+0';$('pnlPct').textContent='0%';$('trades').textContent='0';$('winRate').textContent='0%';renderPositions();drawChart();saveState();logMsg('เปลี่ยนพอร์ต '+pf);}

function buy(sym){
  logMsg('BUY CLICK '+sym);
  if(positions[sym]){logMsg('มี '+sym+' แล้ว');return;}
  var price=prices[sym],atr=atrs[sym];
  var sh=calcShares(price,atr);
  positions[sym]={shares:sh,entry:price,sl:price-1.2*atr,tp:price+3.5*atr};
  renderPositions();drawChart();saveState();
  logMsg('BUY '+sym+' '+sh+' @'+price);
}
function sell(sym){
  if(!positions[sym])return;
  var pos=positions[sym];
  var isWin=Math.random()>0.35;
  var exit=isWin?pos.entry+(Math.random()*0.3+0.7)*(pos.tp-pos.entry):pos.entry-(Math.random()*0.3+0.2)*(pos.entry-pos.sl);
  var net=(exit-pos.entry)*pos.shares-(pos.entry*pos.shares)*0.0011;
  pnl+=net;trades++;if(net>0)wins++;equity.push(equity[equity.length-1]+net);
  $('totalPnl').textContent=(pnl>=0?'+':'')+pnl.toFixed(2);$('pnlPct').textContent=((pnl/pf)*100).toFixed(2)+'%';$('trades').textContent=trades;$('winRate').textContent=Math.round(wins/Math.max(1,trades)*100)+'%';
  delete positions[sym];renderPositions();drawChart();saveState();
  logMsg('SELL '+sym+' Net '+net.toFixed(2)+' Total '+pnl.toFixed(2));
}
function closeAll(){Object.keys(positions).forEach(function(s){sell(s);});}
function hardReset(){if(!confirm('RESET?'))return;pf=500;pnl=0;trades=0;wins=0;equity=[500];positions={};try{localStorage.removeItem('ai_core_final_static');}catch(e){}$('pfRange').value=pf;$('pfVal').textContent=pf;$('tierLbl').textContent=getTier(pf);$('totalPnl').textContent='+0';$('trades').textContent='0';$('winRate').textContent='0%';renderPositions();drawChart();logMsg('RESET DONE');}

function toggleAuto(){
  auto=!auto;
  var b=$('startBtn');b.textContent=auto?'⏸ STOP AUTO':'🚀 START AUTO BOOST v3 10%';b.style.background=auto?'#ff4444':'#ff66ff';
  if(!auto){logMsg('STOPPED P&L '+pnl.toFixed(2));return;}
  logMsg('AUTO STARTED พอร์ต '+pf+'฿');
  (function loop(){if(!auto)return;try{if(Object.keys(positions).length>0&&Math.random()>0.5){var held=Object.keys(positions);sell(held[Math.floor(Math.random()*held.length)]);}else{var syms=Object.keys(prices);var sym=syms[Math.floor(Math.random()*syms.length)];if(!positions[sym])buy(sym);}}catch(e){logMsg('ERR '+e.message);}setTimeout(loop,1500);})();
}

function init(){
  try{
    logMsg('INIT START STATIC MODE');
    $('pfRange').addEventListener('input', function(){changePortfolio(this.value);});
    $('startBtn').addEventListener('click', toggleAuto);
    var restored=loadState();
    if(!restored){$('pfRange').value=pf;$('pfVal').textContent=pf;$('tierLbl').textContent=getTier(pf);}
    renderPositions();drawChart();
    logMsg('INIT OK - STATIC MODE หุ้นอยู่ใน HTML เลย กดได้แน่นอน มีพอร์ต มีเซฟ');
  }catch(e){logMsg('INIT ERROR '+e.message);console.error(e);}
}
if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded', init);}else{init();}
</script>
</body>
</html>
"""
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML_PAGE, headers={"Cache-Control":"no-store"})
@app.get("/health")
def health():
    return {"ok": True, "mode": "FINAL STATIC PORT SAVE"}
