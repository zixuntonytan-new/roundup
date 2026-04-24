from bs4 import BeautifulSoup
from .base import get_soup, get_json, pack

def scrape() -> list:
    url = "https://www.frbsf.org/wp-json/wp/v2/sffed_publications?publication-type=1979&per_page=10"
    try:
        entries = get_json(url)
    except Exception as e:
        print(f"[WP] FED-SANFRANCISCO fetch error: {e}")
        return []
    data = []
    for wp in entries:
        try:
            title = wp["title"]["rendered"]
            link = wp["link"]
            date = wp["date"].split("T")[0].strip()
            author = wp["meta"].get("publication_authors", "")
            if not author:
                ls = get_soup(link)
                divs = ls.find_all("div", {"sffed-associated-person"})
                author = ", ".join(d.get_text().strip() for d in divs if d.get_text().strip())
            abstract_soup = BeautifulSoup(wp["content"]["rendered"], "html.parser")
            p = abstract_soup.find("p")
            abstract = p.text.strip() if p else ""
            data.append(pack("FED-SANFRANCISCO", title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-SANFRANCISCO entry error: {e}")
    return data
