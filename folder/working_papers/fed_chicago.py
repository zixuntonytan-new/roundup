import time
from .base import get_soup, pack

def scrape() -> list:
    s = get_soup("https://www.chicagofed.org/publications/publication-listing?filter_series=18")
    data = []
    for el in s.find_all("div", {"class": "cfedPublicationListing"}):
        try:
            a = el.find("a", {"class": "cfedPublicationListing--title"})
            title = a.text.strip()
            link = "https://www.chicagofed.org" + a["href"]
            info = el.find("div", {"class": "cfedPublicationListing--info"}).text.strip().split("|")
            author = info[0].strip()
            date = info[4].strip() + " " + info[1].strip() if len(info) > 4 else ""
            time.sleep(1)
            ls = get_soup(link)
            abstract_el = ls.find("div", {"class": "cfedArticle__introParagraph"})
            abstract = abstract_el.text.strip() if abstract_el else ""
            data.append(pack("FED-CHICAGO", title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-CHICAGO entry error: {e}")
    return data
