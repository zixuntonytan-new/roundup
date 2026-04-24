import time
from .base import get_soup, pack

def scrape() -> list:
    s = get_soup("https://www.richmondfed.org/publications/research/working_papers")
    data = []
    for el in s.find_all("div", {"class": "data__row"}):
        try:
            title = el.find("div", {"class": "data__title"}).get_text().replace("\n", "").strip()
            author = el.find("div", {"class": "data__authors"}).get_text().replace("\n", "").strip()
            date = el.find("span", {"class": "data__issue"}).text.split(",")[0].strip()
            link = "https://www.richmondfed.org" + el.find("div", {"class": "data__title"}).find("a")["href"]
            time.sleep(1)
            ls = get_soup(link)
            abstract_el = ls.find("div", {"class": "working-paper__abstract"})
            abstract = abstract_el.get_text().strip() if abstract_el else ""
            data.append(pack("FED-RICHMOND", title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-RICHMOND entry error: {e}")
    return data
