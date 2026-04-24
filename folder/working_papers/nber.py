import re, time, requests
from .base import get_soup, get_json, pack, HEADERS

def scrape() -> list:
    url = "https://www.nber.org/api/v1/working_page_listing/contentType/working_paper/_/_/search?page=1&perPage=100"
    elements = get_json(url)["results"]
    data = []
    for el in elements:
        try:
            link = "https://www.nber.org" + el["url"]
            time.sleep(1)
            s = get_soup(link)
            abstract_el = s.find("div", {"class": "page-header__intro-inner"})
            abstract = abstract_el.text.strip() if abstract_el else ""
            raw = s.find("div", {"class": "page-header__authors js-expandable-list"})
            author = re.sub(r"\s+", " ", raw.text.strip()) if raw else ""
            # Use None for published_at so the DB uses fetched_at (today) instead of
            # a fake month-start date from the displaydate field (e.g. "April 2025" -> April 1)
            data.append({
                "source": "NBER",
                "title": el["title"],
                "url": link,
                "summary": f"{author}\n\n{abstract}".strip(),
                "published_at": None,
            })
        except Exception as e:
            print(f"[WP] NBER entry error: {e}")
    return data
