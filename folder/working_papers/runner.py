"""
Master runner for the Academic Desk working papers collector.
To disable a scraper temporarily, comment out its entry in the group it belongs to.

Scrapers run in four groups — each can be triggered independently via the API:
  CONCURRENT  — single-request scrapers, all at once       /admin/collect/academic/feeds
  THREADED    — per-paper scrapers, 3 workers              /admin/collect/academic/papers
  SEQUENTIAL  — Selenium scrapers, one Chrome at a time    /admin/collect/academic/selenium
  (all three) —                                            /admin/collect/academic
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Headline

from .nber             import scrape as scrape_nber
from .bea              import scrape as scrape_bea
from .bis              import scrape as scrape_bis
from .boe              import scrape as scrape_boe
from .imf              import scrape as scrape_imf
from .fed_atlanta      import scrape as scrape_fed_atlanta
from .fed_board        import scrape as scrape_fed_board
from .fed_board_notes  import scrape as scrape_fed_board_notes
from .fed_chicago      import scrape as scrape_fed_chicago
from .fed_cleveland    import scrape as scrape_fed_cleveland
from .fed_dallas       import scrape as scrape_fed_dallas
from .fed_new_york     import scrape as scrape_fed_new_york
from .fed_philadelphia import scrape as scrape_fed_philadelphia
from .fed_richmond     import scrape as scrape_fed_richmond
from .fed_san_francisco import scrape as scrape_fed_san_francisco
from .ecb              import scrape as scrape_ecb
from .fedinprint import (
    scrape_boston      as scrape_fed_boston,
    scrape_kansascity  as scrape_fed_kansas_city,
    scrape_minneapolis as scrape_fed_minneapolis,
    scrape_stlouis     as scrape_fed_st_louis,
)

# ── Single HTTP request each ───────────────────────────────────────────────────
CONCURRENT = [
    ("BEA",             scrape_bea),
    ("BIS",             scrape_bis),
    ("BOE",             scrape_boe),
    ("IMF",             scrape_imf),
    ("FED-ATLANTA",     scrape_fed_atlanta),
    ("FED-BOARD",       scrape_fed_board),
    ("FED-BOARD-NOTES", scrape_fed_board_notes),
    ("FED-BOSTON",      scrape_fed_boston),
    ("FED-DALLAS",      scrape_fed_dallas),
    ("FED-KANSASCITY",  scrape_fed_kansas_city),
    ("FED-MINNEAPOLIS", scrape_fed_minneapolis),
    ("FED-SANFRANCISCO",scrape_fed_san_francisco),
    ("FED-STLOUIS",     scrape_fed_st_louis),
]

# ── Per-paper landing-page requests, 1s sleep each — 3 concurrent ─────────────
THREADED = [
    ("NBER",            scrape_nber),
    ("FED-CHICAGO",     scrape_fed_chicago),
    ("FED-NEWYORK",     scrape_fed_new_york),
    ("FED-PHILADELPHIA",scrape_fed_philadelphia),
    ("FED-RICHMOND",    scrape_fed_richmond),
]

# ── Selenium — one Chrome instance at a time ──────────────────────────────────
SEQUENTIAL = [
    ("FED-CLEVELAND",   scrape_fed_cleveland),
    ("ECB",             scrape_ecb),
]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_seen(db: Session) -> set:
    return {t for (t,) in db.query(Headline.title).filter(Headline.desk == "academic").all()}

def _run(name, fn):
    try:
        papers = list(fn())
        print(f"[WP] {name}: fetched {len(papers)}")
        return name, papers
    except Exception as e:
        print(f"[WP] Error fetching {name}: {e}")
        return name, []

def _insert(db: Session, papers, seen: set) -> int:
    inserted = 0
    for p in papers:
        if p["title"] in seen:
            continue
        h = Headline(
            source=p["source"],
            desk="academic",
            title=p["title"],
            url=p["url"],
            summary=p.get("summary", ""),
            published_at=p.get("published_at"),
        )
        db.add(h)
        try:
            db.commit()
            seen.add(p["title"])
            inserted += 1
        except IntegrityError:
            db.rollback()
    return inserted

def _run_concurrent(db, scrapers, seen) -> int:
    total = 0
    with ThreadPoolExecutor(max_workers=len(scrapers)) as ex:
        futures = {ex.submit(_run, name, fn): name for name, fn in scrapers}
        for fut in as_completed(futures):
            name, papers = fut.result()
            n = _insert(db, papers, seen)
            print(f"[WP] {name}: inserted {n}")
            total += n
    return total

def _run_threaded(db, scrapers, seen, workers=3) -> int:
    total = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_run, name, fn): name for name, fn in scrapers}
        for fut in as_completed(futures):
            name, papers = fut.result()
            n = _insert(db, papers, seen)
            print(f"[WP] {name}: inserted {n}")
            total += n
    return total

def _run_sequential(db, scrapers, seen) -> int:
    total = 0
    for name, fn in scrapers:
        _, papers = _run(name, fn)
        n = _insert(db, papers, seen)
        print(f"[WP] {name}: inserted {n}")
        total += n
    return total


# ── Public phase runners (each builds its own seen_titles from DB) ────────────

def run_feeds(db: Session) -> int:
    print("[WP] Feeds: concurrent scrapers")
    n = _run_concurrent(db, CONCURRENT, _get_seen(db))
    print(f"[WP] Feeds done — inserted {n}")
    return n

def run_papers(db: Session) -> int:
    print("[WP] Papers: threaded scrapers (3 workers)")
    n = _run_threaded(db, THREADED, _get_seen(db))
    print(f"[WP] Papers done — inserted {n}")
    return n

def run_selenium(db: Session) -> int:
    print("[WP] Selenium: sequential scrapers")
    n = _run_sequential(db, SEQUENTIAL, _get_seen(db))
    print(f"[WP] Selenium done — inserted {n}")
    return n

def run_working_papers_collector(db: Session) -> int:
    seen = _get_seen(db)
    total = 0
    print("[WP] Phase 1: concurrent scrapers")
    total += _run_concurrent(db, CONCURRENT, seen)
    print("[WP] Phase 2: threaded scrapers (3 workers)")
    total += _run_threaded(db, THREADED, seen)
    print("[WP] Phase 3: Selenium scrapers (sequential)")
    total += _run_sequential(db, SEQUENTIAL, seen)
    print(f"[WP] Done — total inserted: {total}")
    return total
