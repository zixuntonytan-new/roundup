from .base import get_soup, pack

def scrape() -> list:
    s = get_soup("https://www.federalreserve.gov/econres/feds/index.htm")
    data = []
    for el in s.select("div.col-xs-12.col-md-9.heading:not([style])"):
        try:
            title = el.select_one("h5 > a").text.strip()
            link = "https://www.federalreserve.gov" + el.select_one("h5 > a")["href"]
            author = el.select_one("div.authors").text.strip()
            abstract = el.select_one("div.collapse > p").text.strip().replace("Abstract: ", "")
            date = el.select_one("time")["datetime"]
            data.append(pack("FED-BOARD", title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-BOARD entry error: {e}")
    return data
