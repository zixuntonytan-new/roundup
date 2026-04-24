import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .base import get_soup, pack, HEADERS

def scrape() -> list:
    current_year = datetime.now().year
    payload = {
        "csrfmiddlewaretoken": "", "archive-topics-search-input": "",
        "archive-authors-search-input": "",
        "archive-years": str(current_year),
        "archive-years-search-input": "", "sortby": "date", "order": "desc",
        "years": str(current_year),
        "pageNumber": "1", "perPageCount": "5",
    }
    headers = {
        "Origin": "https://www.kansascityfed.org",
        "Referer": "https://www.kansascityfed.org/research/research-working-papers/research-working-paper-archive/",
        "User-Agent": HEADERS["User-Agent"],
    }
    url = "https://www.kansascityfed.org/research/research-working-papers/research-working-paper-archive/"
    try:
        r = requests.post(url, headers=headers, data=payload, files=[], timeout=60)
        r.raise_for_status()
        resp = r.json()
    except Exception as e:
        print(f"[WP] FED-KANSASCITY fetch error: {e}")
        return []
    soup = BeautifulSoup(resp["rows"], "html.parser")
    data = []
    for el in soup.find_all("h4"):
        try:
            title = el.text.strip()
            landing = "https://www.kansascityfed.org" + el.find("a")["href"]
            ls = get_soup(landing)
            date = ls.find("time").get("datetime", "").strip()
            author = ls.find("div", {"class": "article-author"}).get_text().split("by:")[1].strip()
            tags = ls.find_all(attrs={"data-block-key": True})
            abstract = tags[1].get_text(strip=True) if len(tags) >= 2 else ""
            data.append(pack("FED-KANSASCITY", title, landing, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-KANSASCITY entry error: {e}")
    return data
