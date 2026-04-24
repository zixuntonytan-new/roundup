import time
from datetime import datetime
from .base import get_soup, get_json, pack

def scrape() -> list:
    current_year = datetime.now().year
    data = []
    for year in [current_year, current_year - 1]:
        try:
            url = f"https://www.newyorkfed.org//api/research/getsritemshtml?year={year}&useLucene=true"
            entries = get_json(url)
            for entry in entries:
                try:
                    title = (entry.get("Paper_Title") or "").strip()
                    author = (entry.get("AuthorsHtml") or "").strip()
                    date = entry.get("PublicationDate") or ""
                    if not entry.get("Uri"):
                        continue
                    link = "https://www.newyorkfed.org/" + entry["Uri"]
                    time.sleep(1)
                    ls = get_soup(link)
                    article_divs = ls.select("div.ts-article-text")
                    abstract = article_divs[1].text.strip().replace("\n", " ") if len(article_divs) > 1 else ""
                    data.append(pack("FED-NEWYORK", title, link, author, abstract, date))
                except Exception as e:
                    print(f"[WP] FED-NEWYORK entry error: {e}")
        except Exception as e:
            print(f"[WP] FED-NEWYORK year {year} error: {e}")
    return data
