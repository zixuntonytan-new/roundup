import time
from datetime import datetime
from .base import get_soup, post_json, pack, HEADERS

def scrape() -> list:
    current_year = datetime.now().year
    years = [current_year, current_year - 1] if datetime.now().month == 1 else [current_year]
    api_url = "https://www.bostonfed.org/api/pubsanddata/publications"
    data = []
    for year in years:
        try:
            headers = {"Accept": "application/json", "User-Agent": HEADERS["User-Agent"]}
            payload = {
                "yr": str(year), "jel": "", "type": "",
                "series": "8c2cb55e251349c59d19db1040c20368",
                "vol": "", "siteTpc": "", "dept": "", "author": "", "focus": "",
                "program": "", "services": "", "center": "", "yrFrom": "", "yrTo": "",
                "d": "false", "dt": "false", "srt": "0", "pgSz": "20", "pgN": "1",
            }
            resp = post_json(api_url, headers=headers, data=payload)
            if isinstance(resp, list):
                entries = resp
            elif isinstance(resp, dict):
                entries = resp.get("publications") or resp.get("data") or resp.get("results") or []
            else:
                print(f"[WP] FED-BOSTON unexpected response type: {type(resp)}")
                continue
            for entry in entries:
                try:
                    title = entry.get("title") or entry.get("Title") or entry.get("name") or ""
                    if not title:
                        print(f"[WP] FED-BOSTON: no title key, available keys: {list(entry.keys())[:10]}")
                        continue
                    raw_authors = entry.get("itemAuthors") or entry.get("authors") or []
                    author = ", ".join(
                        (a.get("fullName") or a.get("name") or str(a))
                        for a in raw_authors
                    )
                    link = "https://www.bostonfed.org/" + entry["url"]
                    time.sleep(1)
                    ls = get_soup(link)
                    abstract = ls.find("div", {"id": "collapse3"}).get_text().strip()
                    number_el = ls.find("p", {"class": "doi-text"})
                    meta = ls.find("meta", {"property": "article:published_time"})
                    date = meta["content"].split("T")[0] if meta else ""
                    data.append(pack("FED-BOSTON", title, link, author, abstract, date))
                except Exception as e:
                    print(f"[WP] FED-BOSTON entry error: {e}")
        except Exception as e:
            print(f"[WP] FED-BOSTON year {year} error: {e}")
    return data
