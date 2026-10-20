import threading, time, logging
log = logging.getLogger("scheduler")
_stop = threading.Event()
_thr = None

def _loop(config_path, trade_log_path, min_trades, check_hours):
    interval = max(60, int(check_hours) * 3600)
    log.info(f"scheduler started interval={interval}s min_trades={min_trades}")
    while not _stop.wait(interval):
        log.info("scheduler tick (TODO: rebalance logic)")

def start_scheduler(config_path, trade_log_path, min_trades=30, check_hours=24):
    global _thr
    _stop.clear()
    _thr = threading.Thread(target=_loop, args=(config_path, trade_log_path, min_trades, check_hours), daemon=True)
    _thr.start()
    return _thr

def stop_scheduler():
    _stop.set()
    if _thr: _thr.join(timeout=5)
    log.info("scheduler stopped")
