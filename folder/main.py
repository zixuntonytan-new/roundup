from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

from app.database import startup, SessionLocal
from app.scheduler import start_scheduler
from app.routes import series, headlines
from app.collectors.rss import run_rss_collector
from app.collectors.fred import run_fred_collector
from app.collectors.working_papers import (
    run_working_papers_collector,
    run_feeds,
    run_papers,
    run_selenium,
)
from app.routes.calendar import router as calendar_router

load_dotenv()

app = FastAPI(title="Macro Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(series.router)
app.include_router(headlines.router)
app.include_router(calendar_router)


@app.on_event("startup")
def on_startup():
    startup()
    # start_scheduler()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/admin/collect/rss")
def trigger_rss():
    db = SessionLocal()
    try:
        n = run_rss_collector(db)
        return {"inserted": n}
    finally:
        db.close()


@app.get("/admin/collect/fred")
def trigger_fred():
    db = SessionLocal()
    try:
        run_fred_collector(db)
        return {"status": "ok"}
    finally:
        db.close()


@app.get("/admin/collect/academic")
def trigger_academic():
    db = SessionLocal()
    try:
        n = run_working_papers_collector(db)
        return {"inserted": n}
    finally:
        db.close()

@app.get("/admin/collect/academic/feeds")
def trigger_academic_feeds():
    db = SessionLocal()
    try:
        n = run_feeds(db)
        return {"inserted": n}
    finally:
        db.close()

@app.get("/admin/collect/academic/papers")
def trigger_academic_papers():
    db = SessionLocal()
    try:
        n = run_papers(db)
        return {"inserted": n}
    finally:
        db.close()

@app.get("/admin/collect/academic/selenium")
def trigger_academic_selenium():
    db = SessionLocal()
    try:
        n = run_selenium(db)
        return {"inserted": n}
    finally:
        db.close()


@app.get("/admin/collect/calendar")
def trigger_calendar():
    from app.collectors.calendar_bea import run_bea_calendar_collector
    db = SessionLocal()
    try:
        result = run_bea_calendar_collector(db)
        return {"status": "ok", **result}
    finally:
        db.close()


# Serve frontend files explicitly — no catch-all mount so API routes are never shadowed
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/main.js")
def serve_main_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "main.js"))

@app.get("/style.css")
def serve_style_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "style.css"))

@app.get("/calendar.js")
def serve_calendar_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "calendar.js"))

@app.get("/calendar.css")
def serve_calendar_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "calendar.css"))
