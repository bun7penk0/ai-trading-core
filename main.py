from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI()

HTML_PAGE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI CORE BOOST v3 WORKING</title>
<style>
body{margin:0;background:#070a0e;color:#e6e6e6;font-family:system-ui}
.hd{padding:14px;background:#0f1518;border-bottom:2px solid #ff66ff;position:sticky;top:0}
.card{background:#12181b;border:1px solid #2a3a3e;border-radius:14px;padding:14px;margin:10px}
.dim{color:#7a8a8e;font-size:12px}
.btn{padding:14px;border-radius:12px;border:0;font-weight:900;cursor:pointer;font-size:15px;margin:3px}
.btn-v3{background:#ff66ff;color:#000;width:100%}
.btn-g{background:#00ff88;color:#000}
.btn-d{background:#1e2e32;color:#fff}
.btn-r{background:#ff4444;color:#fff}
.stock{display:flex;justify-content:space-between;align-items:center;background:#182226;border-radius:10px;padding:14px;margin:8px 0;border:1px solid #2a3a3e}
#log{background:#000;color:#00ff88;padding:12px;border-radius:8px;font-size:12px;height:180px;overflow:auto;border:1px solid #333;white-space:pre-wrap}
canvas{background:#0e1618;border-radius:10px;width:100%;height:200px;display:block}
</style>
</head>
<body>
<div class="hd"><b>AI CORE BOOST v3 WORKING 100% ✅</b><br><span class="dim">กดติดแน่นอน - ไม่มี localStorage</span></div>

<div class="card">
<div style="display:flex;gap:8px">
<div style="flex:1;background:#182226;border-radius:10px;padding:12px;text-align:center"><div class="dim">P&L</div><b id="totalPnl" style="color:#ff66ff;font-size:22px">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:12px;text-align:center"><div class="dim">WIN</div><b id="winRate" style="font-size:22px">0%</b></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:12px;text-align:center"><div class="dim">TRADES</div><b id="trades" style="font-size:22px">0</b></div>
</div>
</div>

<div class="card"><canvas id="chart" width="400" height="200"></canvas></div>
<div class="card"><div class="dim">POSITIONS</div><div id="positions">ยังไม่มี</div></div>

<div class="card">
<button class="btn btn-v3" id="startBtn" onclick="toggleAuto()">🚀 START AUTO BOOST v3 10% - กดตรงนี้</button>
<div style="display:flex;gap:6px;margin-top:10px">
<button class="btn btn-d" onclick="testBuy()">TEST BUY PTT</button>
<button class="btn btn-d" onclick="closeAll()">Close All</button>
<button class="btn btn-r" onclick="hardReset()">RESET</button>
</div>
<pre id="log">Ready - กด START ได้เลย
</pre>
</div>

<div class="card">
<b>STOCKS - กด BUY ได้เลย (8 ตัว)</b>
<div id="stocks"></div>
</div>

<script>
var pf = 500; var auto = false; var equity = [500]; var pnl = 0; var trades = 0; var wins = 0; var positions = {};
var STOCKS_DATA = {
  "PTT": {price: 32.5, atr: 0.8},
  "AOT": {price: 58.25, atr: 1.5},
  "CPALL": {price: 62, atr: 1.2},
  "SCB": {price: 110, atr: 2},
  "DELTA": {price: 80, atr: 2},
  "ADVANC": {price: 220, atr: 2.5},
  "BDMS": {price: 28, atr: 0.6},
  "PTTEP": {price: 150, atr: 3}
};
function logMsg(m){ var l = document.getElementById('log'); var time = new Date().toLocaleTimeString(); l.innerText = time + ' ' + m + '\\n' + l.innerText; }
function calcShares(price, atr){ var risk = pf * 0.035; var stop = 1.2 * atr; var shares = risk / stop; shares = Math.floor(shares); if(shares < 1) shares = 1; if(shares > 20) shares = 20; return shares; }
function renderStocks(){
  var html = '';
  for(var sym in STOCKS_DATA){
    var s = STOCKS_DATA[sym]; var sh = calcShares(s.price, s.atr); var sl = (s.price - 1.2 * s.atr).toFixed(2); var tp = (s.price + 3.5 * s.atr).toFixed(2);
    html += '<div class="stock"><div><b>' + sym + '</b><br><span class="dim">' + s.price + '฿ SL ' + sl + ' TP ' + tp + '</span></div><div><button class="btn btn-g" onclick="buy(\\'' + sym + '\\')">BUY ' + sh + '</button></div></div>';
  }
  document.getElementById('stocks').innerHTML = html;
}
function renderPositions(){
  var count = Object.keys(positions).length; var el = document.getElementById('positions');
  if(count === 0){ el.innerHTML = 'ยังไม่มี - กด BUY ด้านล่างได้เลย'; return; }
  var html = ''; for(var sym in positions){ var p = positions[sym]; html += '<div style="display:flex;justify-content:space-between;background:#12261c;padding:10px;margin:4px 0;border-radius:8px"><span><b>' + sym + '</b> ' + p.shares + 'sh @' + p.entry + '</span><button class="btn btn-d" onclick="sell(\\'' + sym + '\\')">SELL</button></div>'; }
  el.innerHTML = html;
}
function drawChart(){
  var c = document.getElementById('chart'); var ctx = c.getContext('2d'); var W = c.width, H = c.height; ctx.clearRect(0,0,W,H); ctx.fillStyle = '#0e1618'; ctx.fillRect(0,0,W,H);
  if(equity.length < 2){ ctx.fillStyle = '#666'; ctx.fillText('กด START เพื่อเริ่ม', 10, 20); return; }
  var min = Math.min.apply(null, equity); var max = Math.max.apply(null, equity); var pad = (max - min) * 0.2; if(pad < 5) pad = 5; min -= pad; max += pad;
  ctx.strokeStyle = '#ff66ff'; ctx.lineWidth = 3; ctx.beginPath();
  for(var i=0;i<equity.length;i++){ var x = i / (equity.length - 1) * W; var y = H - ((equity[i] - min) / (max - min)) * H * 0.8 - H*0.1; if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y); }
  ctx.stroke();
}
function buy(sym){
  if(positions[sym]) return; var s = STOCKS_DATA[sym]; var sh = calcShares(s.price, s.atr); var sl = s.price - 1.2 * s.atr; var tp = s.price + 3.5 * s.atr;
  positions[sym] = {shares: sh, entry: s.price, sl: sl, tp: tp}; renderPositions(); drawChart(); logMsg('BUY ' + sym + ' ' + sh);
}
function sell(sym){
  if(!positions[sym]) return; var pos = positions[sym]; var isWin = Math.random() > 0.35; var exitPrice; if(isWin){ exitPrice = pos.entry + (Math.random()*0.3+0.7)*(pos.tp-pos.entry); }else{ exitPrice = pos.entry - (Math.random()*0.3+0.2)*(pos.entry-pos.sl); }
  var gross = (exitPrice - pos.entry) * pos.shares; var fee = (pos.entry * pos.shares) * 0.0011; var net = gross - fee; pnl += net; trades++; if(net > 0) wins++; equity.push(equity[equity.length-1] + net);
  document.getElementById('totalPnl').innerText = (pnl>=0?'+':'') + pnl.toFixed(2); document.getElementById('pnlPct').innerText = ((pnl/pf)*100).toFixed(2) + '%'; document.getElementById('trades').innerText = trades; document.getElementById('winRate').innerText = Math.round(wins/Math.max(1,trades)*100) + '%';
  delete positions[sym]; renderPositions(); drawChart(); logMsg('SELL ' + sym + ' Net ' + net.toFixed(2) + ' Total ' + pnl.toFixed(2));
}
function testBuy(){ logMsg('TEST CLICK WORKING!'); buy('PTT'); }
function closeAll(){ for(var sym in positions){ sell(sym); } }
function hardReset(){ pf=500; pnl=0; trades=0; wins=0; equity=[500]; positions={}; try{localStorage.clear();}catch(e){} document.getElementById('totalPnl').innerText='+0'; document.getElementById('trades').innerText='0'; document.getElementById('winRate').innerText='0%'; renderPositions(); drawChart(); logMsg('RESET DONE'); }
function toggleAuto(){
  auto = !auto; var b = document.getElementById('startBtn'); b.innerText = auto ? '⏸ STOP AUTO' : '🚀 START AUTO BOOST v3 10% - กดตรงนี้'; b.style.background = auto ? '#ff4444' : '#ff66ff';
  if(auto){ logMsg('AUTO STARTED'); var loop = async function(){ while(auto){ if(Object.keys(positions).length > 0 && Math.random() > 0.5){ var held = Object.keys(positions); var pick = held[Math.floor(Math.random()*held.length)]; sell(pick); }else{ var syms = Object.keys(STOCKS_DATA); var sym = syms[Math.floor(Math.random()*syms.length)]; if(!positions[sym]) buy(sym); } await new Promise(function(r){ setTimeout(r, 1500); }); } }; loop(); }else{ logMsg('STOPPED P&L ' + pnl.toFixed(2)); }
}
window.onload = function(){ renderStocks(); renderPositions(); drawChart(); logMsg('INIT OK - กด TEST BUY PTT ได้เลย'); };
</script>
</body>
</html>
"""
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML_PAGE, headers={"Cache-Control":"no-store"})
@app.get("/health")
def health():
    return {"ok":True,"mode":"WORKING"}
