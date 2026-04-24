from datetime import datetime
from .base import get_soup, pack

def scrape() -> list:
    current_year = datetime.now().year
    current_month = datetime.now().month
    urls = ["https://www.federalreserve.gov/econres/notes/feds-notes/default.htm"]
    if current_month == 1:
        urls.append(f"https://www.federalreserve.gov/econres/notes/feds-notes/{current_year - 1}-index.htm")
    data = []
    for url in urls:
        try:
            s = get_soup(url)
            for el in s.select("div.col-xs-12.col-md-9.heading.feds-note:not([style])"):
                try:
                    title = el.find("h5").text.strip()
                    author = el.find("div", class_="authors").text.strip()
                    date = el.find("time")["datetime"]
                    abstract = el.find_all("p")[1].text.strip()
                    href = "https://www.federalreserve.gov/" + el.find("h5").find("a")["href"]
                    data.append(pack("FED-BOARD-NOTES", title, href, author, abstract, date))
                except Exception as e:
                    print(f"[WP] FED-BOARD-NOTES entry error: {e}")
        except Exception as e:
            print(f"[WP] FED-BOARD-NOTES page error {url}: {e}")
    return data
