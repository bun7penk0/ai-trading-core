@app.get("/", response_class=HTMLResponse)
async def root():
    # FIX: must return HTML not JSON - this was the bug causing screenshot JSON
    return HTMLResponse(content=DASH_HTML, status_code=200)

@app.get("/api/live")
async def live():
    # JSON lives here, not at "/"
    return {"status":"LIVE", ...}
