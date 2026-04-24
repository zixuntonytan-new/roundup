from .base import get_soup_js, pack

def scrape() -> list:
    try:
        s = get_soup_js(
            "https://www.clevelandfed.org/publications/working-paper",
            wait_css="li.result-item",
        )
    except Exception as e:
        print(f"[WP] FED-CLEVELAND fetch error: {e}")
        return []
    data = []
    for el in s.find_all("li", {"class": "result-item"}):
        try:
            title = el.find("h5").text.strip()
            link = "https://www.clevelandfed.org" + el.find("h5").find("a")["href"]
            dn = el.find("div", {"class": "date-reference"}).get_text().split("|")
            date = dn[0].strip()
            abstract = el.find("div", {"class": "page-description"}).get_text().strip()
            authors = ", ".join(el.find("div", {"class": "authors"}).get_text().strip().split("\n"))
            data.append(pack("FED-CLEVELAND", title, link, authors, abstract, date))
        except Exception as e:
            print(f"[WP] FED-CLEVELAND entry error: {e}")
    return data
