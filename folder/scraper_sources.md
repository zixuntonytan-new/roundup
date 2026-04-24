# Scraper Sources

All scrapers live in `app/collectors/working_papers/`. Results are inserted into the `headlines` table with `desk='academic'`. The runner (`runner.py`) executes them in four phases — see that file for grouping logic.

---

## Phase 1 — Concurrent (single request each)

| Source | File | Method | URL |
|---|---|---|---|
| BEA | `bea.py` | HTML scrape + per-paper landing page | `https://www.bea.gov/research/papers` |
| BIS | `bis.py` | RSS | `https://www.bis.org/doclist/wppubls.rss?...paging_length=10` |
| BOE | `boe.py` | RSS + per-paper landing page | `https://www.bankofengland.co.uk/rss/publications` |
| IMF | `imf.py` | Firecrawl SDK — renders the JS-heavy IMF publications search page (working papers filter applied via URL hash), returns markdown, parsed with regex. Requires `FIRECRAWL_API_KEY` in `.env`. If results dry up, verify the URL still resolves in a browser. | `https://www.imf.org/en/publications/search?when=After&series=IMF+Working+Papers#cf-type=WRKNGPPRS` |
| FED-ATLANTA | `fed_atlanta.py` | RSS | `https://www.atlantafed.org/rss/wps` |
| FED-BOARD | `fed_board.py` | HTML scrape (single page) | `https://www.federalreserve.gov/econres/feds/index.htm` |
| FED-BOARD-NOTES | `fed_board_notes.py` | HTML scrape (single page) | `https://www.federalreserve.gov/econres/notes/feds-notes/default.htm` |
| FED-BOSTON | `fedinprint.py` | RSS via fedinprint, filtered to Working Papers by `bibo:series` | `https://www.fedinprint.org/rss/boston.rss` |
| FED-DALLAS | `fed_dallas.py` | HTML scrape; downloads PDF per paper to extract date | `https://www.dallasfed.org/research/papers` |
| FED-KANSASCITY | `fedinprint.py` | RSS via fedinprint, filtered to Working Papers by `bibo:series` | `https://www.fedinprint.org/rss/kansascity.rss` |
| FED-MINNEAPOLIS | `fedinprint.py` | RSS via fedinprint, filtered to Working Papers by `bibo:series` | `https://www.fedinprint.org/rss/minneapolis.rss` |
| FED-SANFRANCISCO | `fed_san_francisco.py` | JSON API; falls back to per-paper landing page for authors | `https://www.frbsf.org/wp-json/wp/v2/sffed_publications?publication-type=1979&per_page=10` |
| FED-STLOUIS | `fedinprint.py` | RSS via fedinprint, filtered to Working Papers by `bibo:series` | `https://www.fedinprint.org/rss/stlouis.rss` |

---

## Phase 2 — Threaded, 3 workers (per-paper landing pages, 1s sleep between requests)

| Source | File | Method | URL |
|---|---|---|---|
| NBER | `nber.py` | JSON API for listing + HTML scrape per paper (100 papers) | `https://www.nber.org/api/v1/working_page_listing/contentType/working_paper/_/_/search?page=1&perPage=100` |
| FED-CHICAGO | `fed_chicago.py` | HTML scrape listing + per-paper landing page | `https://www.chicagofed.org/publications/publication-listing?filter_series=18` |
| FED-NEWYORK | `fed_new_york.py` | JSON API (current + prior year) + per-paper landing page | `https://www.newyorkfed.org//api/research/getsritemshtml?year={year}&useLucene=true` |
| FED-PHILADELPHIA | `fed_philadelphia.py` | HTML scrape (JSON embedded in `<script>`) + per-paper landing page | `https://www.philadelphiafed.org/search-results/all-work?searchtype=working-papers` |
| FED-RICHMOND | `fed_richmond.py` | HTML scrape listing + per-paper landing page | `https://www.richmondfed.org/publications/research/working_papers` |

---

## Phase 3 — Sequential (Selenium / headless Chrome)

| Source | File | Method | URL | Wait selector |
|---|---|---|---|---|
| FED-CLEVELAND | `fed_cleveland.py` | Selenium — JS-rendered listing | `https://www.clevelandfed.org/publications/working-paper` | `li.result-item` |
| ECB | `ecb.py` | Selenium — JS-rendered + lazy-loaded listing (first 20 papers) | `https://www.ecb.europa.eu/pub/research/working-papers/html/index.en.html` | `dt[isodate]` |

---

## Disabled

| Source | File | Reason |
|---|---|---|
| BFI | `bfi.py` | 403 — site blocks scrapers |

---

## Shared Infrastructure

| File | Purpose |
|---|---|
| `base.py` | `get_soup()` — plain requests + BeautifulSoup; `get_soup_js()` — headless Chrome via selenium + webdriver-manager; `get_json()`, `post_json()`, `pack()`, `parse_date()` |
| `fedinprint.py` | Shared RSS handler for four Fed banks on fedinprint.org; filters by `bibo:series` to exclude non-working-paper content |
| `runner.py` | Orchestrates all phases; DB writes happen in the main thread after each phase completes |
