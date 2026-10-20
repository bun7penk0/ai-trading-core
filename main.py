from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI()
HTML_PAGE = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI CORE BOOST v3 FINAL SAFE + PORT + SAVE</title>
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
<div class="hd"><b>AI CORE • BOOST v3 FINAL SAFE ✅</b><br><span class="dim">SAFE no-inline-onclick + PORT + SAVE + Win 65% TP 3.5 SL 1.2</span></div>
<div class="card">
<div class="dim">เลือกพอร์ต (PORT) - ลากได้ 500฿ ถึง 10,000฿</div>
<input type="range" id="pfRange" min="500" max="10000" step="500" value="500">
<div style="display:flex;justify-content:space-between;align-items:center">
<div><span class="big" id="pfVal">500</span> ฿ <span id="tierLbl" style="color:#ffaa00;font-weight:800">MICRO_500_1k</span></div>
<div style="text-align:right"><span id="saveStatus" style="color:#00ff88;font-size:11px">💾 Ready</span><br><span id="posCount" class="dim">0 pos</span></div>
</div>
<div style="display:flex;gap:8px;margin-top:10px">
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">P&L สุทธิ</div><b id="totalPnl" style="color:#ff66ff;font-size:20px">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">WIN</div><b id="winRate" style="font-size:20px">0%</b><div class="dim">เป้า 65%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">TRADES</div><b id="trades" style="font-size:20px">0</b></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">Avg/ไม้</div><b id="avgTrade" style="font-size:16px">0฿</b></div>
</div>
</div>
<div class="card"><div class="dim">EQUITY CURVE</div><canvas id="chart" width="400" height="200"></canvas><div id="chartInfo" class="dim" style="text-align:right;margin-top:6px"></div></div>
<div class="card"><div class="dim">POSITIONS</div><div id="positions" style="padding:10px;background:#0e1618;border-radius:8px">ยังไม่มี</div></div>
<div class="card">
<button class="btn btn-v3" id="startBtn">🚀 START AUTO BOOST v3 10%</button>
<div style="display:flex;gap:6px;margin-top:8px">
<button class="btn btn-d" id="testBtn">TEST BUY PTT</button>
<button class="btn btn-d" id="saveBtn">💾 SAVE NOW</button>
<button class="btn btn-d" id="closeAllBtn">Close All</button>
<button class="btn btn-r" id="resetBtn">RESET</button>
</div>
<pre id="log">Ready...</pre>
</div>
<div class="card">
<b>STOCKS - SAFE MODE (no inline onclick)</b>
<div id="stocks" style="margin-top:10px">Loading...</div>
</div>
<script>
(function(){
  "use strict";
  var pf = 500, auto = false;
  var equity = [500], pnl = 0, trades = 0, wins = 0;
  var positions = {};
  var STOCKS_DATA = {
    "PTT":{price:32.5,atr:0.8},"AOT":{price:58.25,atr:1.5},
    "CPALL":{price:62,atr:1.2},"SCB":{price:110,atr:2},
    "DELTA":{price:80,atr:2},"ADVANC":{price:220,atr:2.5},
    "BDMS":{price:28,atr:0.6},"PTTEP":{price:150,atr:3}
  };
  function $(id){ return document.getElementById(id); }
  function logMsg(m){ var l = $('log'); if(!l) return; var t = new Date().toLocaleTimeString(); l.textContent = t + ' ' + m + '\n' + l.textContent; }
  function getTier(p){ if(p <= 1000) return "MICRO_500_1k"; return "SMALL_1k_10k"; }
  function calcShares(price, atr){ var riskPct = pf <= 1000 ? 0.035 : 0.025; var risk = pf * riskPct; var stop = 1.2 * atr; var sh = Math.floor(risk / stop); if(sh < 1) sh = 1; if(sh > 25) sh = 25; return sh; }
  function saveState(){ try{ var data = {pf: pf, pnl: pnl, trades: trades, wins: wins, equity: equity, positions: positions}; localStorage.setItem('ai_core_boost_v3_final_safe', JSON.stringify(data)); var el = $('saveStatus'); if(el) el.textContent = '💾 Saved ' + new Date().toLocaleTimeString(); }catch(e){} }
  function loadState(){ try{ var raw = localStorage.getItem('ai_core_boost_v3_final_safe'); if(!raw) return false; var d = JSON.parse(raw); if(!d || typeof d.pf !== 'number') return false; pf = d.pf; pnl = d.pnl||0; trades = d.trades||0; wins = d.wins||0; equity = d.equity||[pf]; positions = d.positions||{}; $('pfRange').value = pf; $('pfVal').textContent = pf.toLocaleString(); $('tierLbl').textContent = getTier(pf); $('totalPnl').textContent = (pnl>=0?'+':'') + pnl.toFixed(2); $('pnlPct').textContent = ((pnl/pf)*100).toFixed(2) + '%'; $('trades').textContent = trades; $('winRate').textContent = (trades?Math.round(wins/trades*100):0) + '%'; $('avgTrade').textContent = (trades?(pnl/trades).toFixed(2):'0') + '฿'; logMsg('RESTORED P&L ' + pnl.toFixed(2) + ' Trades ' + trades); return true; }catch(e){ return false; } }
  function renderStocks(){
    var container = $('stocks'); container.innerHTML = '';
    Object.keys(STOCKS_DATA).forEach(function(sym){
      var s = STOCKS_DATA[sym]; var sh = calcShares(s.price, s.atr); var sl = (s.price - 1.2 * s.atr).toFixed(2); var tp = (s.price + 3.5 * s.atr).toFixed(2);
      var row = document.createElement('div'); row.className = 'stock';
      var left = document.createElement('div'); left.innerHTML = '<b>' + sym + '</b><br><span class="dim">' + s.price + '฿ SL ' + sl + ' TP ' + tp + '</span>';
      var btn = document.createElement('button'); btn.className = 'btn btn-g'; btn.textContent = 'BUY ' + sh; btn.addEventListener('click', function(){ buy(sym); });
      row.appendChild(left); row.appendChild(btn); container.appendChild(row);
    });
    logMsg('renderStocks OK ' + Object.keys(STOCKS_DATA).length + ' ตัว');
  }
  function renderPositions(){
    var el = $('positions'); var syms = Object.keys(positions); $('posCount').textContent = syms.length + ' pos';
    if(syms.length === 0){ el.innerHTML = 'ยังไม่มี - กด BUY ด้านบนได้เลย'; return; }
    el.innerHTML = '';
    syms.forEach(function(sym){
      var p = positions[sym];
      var row = document.createElement('div'); row.style.cssText = 'display:flex;justify-content:space-between;background:#12261c;padding:10px;margin:4px 0;border-radius:8px;align-items:center';
      var span = document.createElement('span'); span.innerHTML = '<b>' + sym + '</b> ' + p.shares + 'sh @' + p.entry;
      var b = document.createElement('button'); b.className = 'btn btn-d'; b.textContent = 'SELL'; b.addEventListener('click', function(){ sell(sym); });
      row.appendChild(span); row.appendChild(b); el.appendChild(row);
    });
  }
  function drawChart(){
    var c = $('chart'), ctx = c.getContext('2d'); var W = c.width, H = c.height; ctx.clearRect(0,0,W,H); ctx.fillStyle = '#0e1618'; ctx.fillRect(0,0,W,H);
    if(equity.length < 2){ ctx.fillStyle = '#666'; ctx.fillText('กด START เพื่อเริ่ม', 10, 20); return; }
    var min = Math.min.apply(null, equity); var max = Math.max.apply(null, equity); var pad = Math.max((max-min)*0.2, 5); min -= pad; max += pad; if(min === max){ min -= 10; max += 10; }
    ctx.strokeStyle = '#ff66ff'; ctx.lineWidth = 3; ctx.beginPath();
    for(var i=0;i<equity.length;i++){ var x = i / (equity.length - 1) * W; var y = H - ((equity[i] - min) / (max - min)) * H * 0.8 - H*0.1; if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y); }
    ctx.stroke(); $('chartInfo').textContent = equity.length + ' pts P&L ' + (equity[equity.length-1]-pf).toFixed(2) + '฿ (' + (((equity[equity.length-1]/pf-1)*100).toFixed(2) + '%) เป้า 10%';
  }
  function changePortfolio(v){
    if(Object.keys(positions).length > 0){ alert('มี Position อยู่ Close All ก่อน'); $('pfRange').value = pf; return; }
    pf = parseInt(v); $('pfVal').textContent = pf.toLocaleString(); $('tierLbl').textContent = getTier(pf); equity = [pf]; pnl = 0; trades = 0; wins = 0; positions = {}; $('totalPnl').textContent = '+0'; $('pnlPct').textContent = '0%'; $('trades').textContent = '0'; $('winRate').textContent = '0%'; $('avgTrade').textContent = '0฿'; renderStocks(); renderPositions(); drawChart(); saveState(); logMsg('เปลี่ยนพอร์ต ' + pf + '฿ ' + getTier(pf));
  }
  function buy(sym){ logMsg('BUY CLICK ' + sym); if(positions[sym]){ logMsg('มี ' + sym + ' แล้ว'); return; } var s = STOCKS_DATA[sym]; var sh = calcShares(s.price, s.atr); var sl = s.price - 1.2 * s.atr; var tp = s.price + 3.5 * s.atr; positions[sym] = {shares: sh, entry: s.price, sl: sl, tp: tp}; renderPositions(); drawChart(); saveState(); logMsg('BUY ' + sym + ' ' + sh + ' @' + s.price); }
  function sell(sym){ logMsg('SELL CLICK ' + sym); if(!positions[sym]){ logMsg('ไม่มี ' + sym); return; } var pos = positions[sym]; var isWin = Math.random() > 0.35; var exit; if(isWin) exit = pos.entry + (Math.random()*0.3+0.7)*(pos.tp-pos.entry); else exit = pos.entry - (Math.random()*0.3+0.2)*(pos.entry-pos.sl); var gross = (exit - pos.entry) * pos.shares; var fee = (pos.entry * pos.shares) * 0.0011; var net = gross - fee; pnl += net; trades++; if(net > 0) wins++; equity.push(equity[equity.length-1] + net); if(equity.length > 100) equity.shift(); $('totalPnl').textContent = (pnl>=0?'+':'') + pnl.toFixed(2); $('pnlPct').textContent = ((pnl/pf)*100).toFixed(2) + '%'; $('trades').textContent = trades; $('winRate').textContent = Math.round(wins/Math.max(1,trades)*100) + '%'; $('avgTrade').textContent = (trades?(pnl/trades).toFixed(2):'0') + '฿'; delete positions[sym]; renderPositions(); drawChart(); saveState(); logMsg('SELL ' + sym + ' @' + exit.toFixed(2) + ' Net ' + net.toFixed(2) + ' ' + (isWin?'WIN':'LOSS')); }
  function closeAll(){ Object.keys(positions).forEach(function(sym){ sell(sym); }); }
  function hardReset(){ if(!confirm('RESET ทั้งหมด? P&L จะหาย')) return; pf=500; pnl=0; trades=0; wins=0; equity=[500]; positions={}; try{ localStorage.removeItem('ai_core_boost_v3_final_safe'); }catch(e){} $('pfRange').value = pf; $('pfVal').textContent = pf; $('tierLbl').textContent = getTier(pf); $('totalPnl').textContent = '+0'; $('pnlPct').textContent = '0%'; $('trades').textContent = '0'; $('winRate').textContent = '0%'; $('avgTrade').textContent = '0฿'; renderPositions(); drawChart(); renderStocks(); logMsg('RESET DONE'); }
  function toggleAuto(){ auto = !auto; var b = $('startBtn'); b.textContent = auto ? '⏸ STOP AUTO' : '🚀 START AUTO BOOST v3 10%'; b.style.background = auto ? '#ff4444' : '#ff66ff'; if(!auto){ logMsg('STOPPED P&L ' + pnl.toFixed(2)); return; } logMsg('AUTO STARTED พอร์ต ' + pf + '฿ BOOST v3'); (function loop(){ if(!auto) return; try{ if(Object.keys(positions).length > 0 && Math.random() > 0.5){ var held = Object.keys(positions); sell(held[Math.floor(Math.random()*held.length)]); } else { var syms = Object.keys(STOCKS_DATA); var sym = syms[Math.floor(Math.random()*syms.length)]; if(!positions[sym]) buy(sym); } } catch(e){ logMsg('ERR ' + e.message); } setTimeout(loop, 1500); })(); }
  function wire(){ $('pfRange').addEventListener('input', function(){ changePortfolio(this.value); }); $('startBtn').addEventListener('click', toggleAuto); $('testBtn').addEventListener('click', function(){ logMsg('TEST CLICK'); buy('PTT'); }); $('saveBtn').addEventListener('click', function(){ saveState(); logMsg('MANUAL SAVE P&L ' + pnl.toFixed(2)); }); $('closeAllBtn').addEventListener('click', closeAll); $('resetBtn').addEventListener('click', hardReset); }
  function init(){ try{ logMsg('INIT START SAFE MODE'); wire(); var restored = loadState(); if(!restored){ $('pfRange').value = pf; $('pfVal').textContent = pf; $('tierLbl').textContent = getTier(pf); } renderStocks(); renderPositions(); drawChart(); logMsg('INIT OK — SAFE MODE พร้อมกด มีพอร์ต มีเซฟ ไม่มี inline onclick'); } catch(e){ logMsg('INIT ERROR: ' + e.message); console.error(e); var el = $('stocks'); if(el) el.innerHTML = 'ERROR: ' + e.message; } }
  if(document.readyState === 'loading'){ document.addEventListener('DOMContentLoaded', init); } else { init(); }
})();
</script>
</body>
</html>
"""
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML_PAGE, headers={"Cache-Control":"no-store"})
@app.get("/health")
def health():
    return {"ok": True, "mode": "FINAL SAFE PORT SAVE BOOST v3"}
