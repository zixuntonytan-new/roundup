# How the Roundup Works: Step-by-Step

## Overview

The Roundup is an automated pipeline that scrapes working papers from 20 economics sources every morning and displays them on a public Streamlit dashboard. The whole process runs without any human intervention after initial setup.

---

## Daily run sequence

### 1. GitHub Actions wakes up at 6:40 AM EST
A scheduled job defined in `.github/workflows/main.yml` triggers automatically every day. It can also be triggered manually from the GitHub website (Actions tab → Daily Run → Run workflow) at any time.

### 2. A fresh Linux environment is provisioned
GitHub spins up a temporary Ubuntu machine, installs Python 3.9, installs Google Chrome + ChromeDriver (needed for JavaScript-heavy sites), and installs all Python packages from `requirements.txt`.

### 3. `run_scraper.py` runs — Part 1: Scraping
The script loops through 20 scraper classes. Each scraper is responsible for one source and implements a `fetch_data()` method. They use four different techniques depending on the source:

- **Plain HTTP + BeautifulSoup** (BEA, BIS, BOE, FED-BOARD, FED-BOARD-NOTES, FED-CHICAGO, FED-DALLAS, FED-NEWYORK, FED-PHILADELPHIA, FED-RICHMOND, FED-SANFRANCISCO): sends a GET request, parses the HTML response.
- **RSS via fedinprint.org** (FED-BOSTON, FED-KANSASCITY, FED-MINNEAPOLIS, FED-STLOUIS, FED-ATLANTA): reads an RSS feed that aggregates working papers from Federal Reserve banks; filters entries where `bibo:series` contains "Working Paper".
- **Selenium headless Chrome** (FED-CLEVELAND, ECB): launches a real browser in the background to handle pages that require JavaScript to render content before it is readable.
- **JSON API** (NBER): calls NBER's internal API endpoint for a listing, then scrapes each paper's landing page for the abstract and author.
- **Firecrawl API** (IMF): calls the Firecrawl cloud service, which renders the IMF's heavily JavaScript-dependent publications page and returns structured markdown. Requires a `FIRECRAWL_API_KEY` set as a GitHub secret.

Each scraper returns a list of dictionaries with: Title, Author, Abstract, Link, Number, Date. The base class (`GenericScraper`) converts this into a pandas DataFrame and creates a unique ID for each paper by combining Source + Number (e.g., `NBER33816`, `ECB2957`).

If a scraper succeeds, it is marked `on` in `streamlit/scraper_status.txt`. If it fails (exception or no data), it is marked `off`. The script continues regardless — a failing scraper does not stop the others.

### 4. All results are concatenated into one DataFrame
After all scrapers run, their individual DataFrames are combined into a single table of all papers seen today.

### 5. `run_scraper.py` runs — Part 2: Deduplication
The `HistoricDataComparer` class loads `data/wp_ids.txt`, which is a Python set containing the IDs of every paper ever seen since the project started (~5,800+ entries). It computes the set difference: papers in today's scrape that are not in the historic set. These are the genuinely new papers.

### 6. New papers are saved
If any new papers were found:
- Their rows are appended to `data/wp_data.csv` — the permanent database.
- Their IDs are appended to `data/wp_ids.txt` — the deduplication set.
- A local HTML preview is saved to `data/local_scrape_outcomes/` (not committed to the repo).

Regardless of whether new papers were found, `streamlit/last_run.txt` is updated with today's date and the count of new papers.

### 7. Git commits and pushes the changes
After the script finishes, the workflow commits all changed files (`wp_data.csv`, `wp_ids.txt`, `scraper_status.txt`, `last_run.txt`) with the message `run (MM/DD/YYYY)` and pushes to the `debug-gh-actions` branch on GitHub. If nothing changed (no new papers, no status changes), Git skips the commit.

### 8. Streamlit reads the updated files
The Streamlit app at `hutchins-roundup.streamlit.app` reads three files directly from the `debug-gh-actions` branch on GitHub using raw file URLs:

- `data/wp_data.csv` — all papers to display
- `streamlit/scraper_status.txt` — which scrapers are currently active
- `streamlit/last_run.txt` — when the last run occurred and how many papers were added

Streamlit caches these reads and refreshes periodically, so the dashboard typically reflects the day's new papers by 7:00 AM EST.

---

## What the dashboard shows

- **Sidebar:** date range slider (1–30 days), source filter, last run date/count, per-scraper on/off status
- **Main panel:** papers from selected sources within the chosen date window, ordered by source (NBER first, then Fed banks, then international sources), each with title (linked), author, estimated publication date, official posted date, and abstract

---

## When things go wrong

- If a scraper fails, it is marked `off` in the dashboard sidebar. The rest of the run continues normally.
- If the entire run fails (e.g., a Python import error), GitHub Actions marks the workflow as failed and sends an email to the repository owner. No data is committed.
- You can manually re-trigger a run any time from the GitHub Actions tab without touching any code.

---

## Key files at a glance

| File | Purpose |
|---|---|
| `run_scraper.py` | Entry point — orchestrates all scrapers and saves results |
| `src/scraper/generic_scraper.py` | Base class all scrapers inherit from |
| `src/scraper/sites/` | One file per source (20 scrapers) |
| `src/scraper/sites/_fedinprint.py` | Shared RSS helper for fedinprint-based scrapers |
| `src/scraper/external_requests.py` | HTTP/Selenium helpers used by scrapers |
| `src/data_comparer.py` | Deduplication logic |
| `data/wp_data.csv` | Full historical database of all papers |
| `data/wp_ids.txt` | Set of all seen paper IDs (fast dedup lookup) |
| `streamlit/app.py` | The web dashboard |
| `streamlit/scraper_status.txt` | Per-scraper on/off status |
| `streamlit/last_run.txt` | Date and new-paper count from last run |
| `.github/workflows/main.yml` | Automated daily schedule + manual trigger |
