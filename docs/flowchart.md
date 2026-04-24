# Data Flow: Websites → Streamlit

```mermaid
flowchart TD

    %% Trigger
    GHA["⏰ GitHub Actions\nScheduled: 6:40 AM EST daily\nor manually triggered"]

    GHA --> RS["run_scraper.py\nOrchestration script"]

    %% Scraper groups
    RS --> G1["Plain HTTP + BeautifulSoup\nBEA · BIS · BOE\nFED-BOARD · FED-BOARD-NOTES\nFED-CHICAGO · FED-DALLAS\nFED-NEWYORK · FED-PHILADELPHIA\nFED-RICHMOND · FED-SANFRANCISCO"]

    RS --> G2["RSS (fedinprint.org)\nFED-BOSTON · FED-KANSASCITY\nFED-MINNEAPOLIS · FED-STLOUIS\nFED-ATLANTA"]

    RS --> G3["Selenium (headless Chrome)\nFED-CLEVELAND · ECB"]

    RS --> G4["JSON API + HTML\nNBER"]

    RS --> G5["Firecrawl API\nIMF\n(requires FIRECRAWL_API_KEY secret)"]

    %% Combine
    G1 --> DF["Combined DataFrame\nTitle · Author · Abstract\nLink · Number · Date · Source"]
    G2 --> DF
    G3 --> DF
    G4 --> DF
    G5 --> DF

    %% Compare
    DF --> CMP["HistoricDataComparer\ncompare() — set difference\nvs. historic IDs"]

    IDS["data/wp_ids.txt\nHistoric paper IDs\n~5,800+ entries"] --> CMP

    %% Branch on novel papers
    CMP -->|"Novel papers found"| SAVE["Save new papers\n→ data/wp_data.csv  (append rows)\n→ data/wp_ids.txt  (append IDs)\n→ streamlit/scraper_status.txt  (on/off per source)\n→ streamlit/last_run.txt  (date + count)"]
    CMP -->|"No new papers"| NOCHANGE["Only last_run.txt updated"]

    SAVE --> GIT["Git commit & push\n'run (MM/DD/YYYY)'"]
    NOCHANGE --> GIT

    GIT --> REPO["GitHub Repository\nbranch: debug-gh-actions"]

    %% Streamlit reads
    REPO -->|"wp_data.csv"| ST["🌐 Streamlit App\nhutchins-roundup.streamlit.app"]
    REPO -->|"scraper_status.txt"| ST
    REPO -->|"last_run.txt"| ST

    ST --> USER["👤 User\nFilters by source & date range\nReads titles, authors, abstracts"]
```

## Key files updated each run

| File | What changes |
|---|---|
| `data/wp_data.csv` | New paper rows appended |
| `data/wp_ids.txt` | New paper IDs appended |
| `streamlit/scraper_status.txt` | `on`/`off` per scraper |
| `streamlit/last_run.txt` | Run date + new paper count |
