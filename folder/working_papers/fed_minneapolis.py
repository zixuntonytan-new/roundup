import re
from .base import get_soup, pack

def scrape() -> list:
    try:
        s = get_soup("https://www.minneapolisfed.org/economic-research/working-papers")
    except Exception as e:
        print(f"[WP] FED-MINNEAPOLIS fetch error: {e}")
        return []
    els = s.select(".i9-c-related-content__group--item")
    if not els:
        els = s.select("article") or s.select(".research-listing__item")
    data = []
    for el in list(els)[:10]:
        try:
            title_el = (el.select_one(".i9-c-related-content__group--title")
                        or el.select_one("h3 a") or el.select_one("h2 a") or el.find("a"))
            if not title_el:
                continue
            title = title_el.text.strip()
            href = title_el.get("href", "")
            if not href:
                continue
            link = "https://www.minneapolisfed.org" + href if href.startswith("/") else href
            ls = get_soup(link)
            date_el = ls.select_one(".i9-c-title-banner__title--date")
            parts = re.split("Published|Revised", date_el.text if date_el else "")
            date = parts[1].strip() if len(parts) > 1 else ""
            abstract_el = ls.find("p", class_="i9-e-p__large i9-js-markdown")
            abstract = abstract_el.text.strip() if abstract_el else ""
            author_divs = ls.find_all("div", class_="i9-c-person-block--small__content--name")
            author = ", ".join(d.find("a").text.strip() for d in author_divs if d.find("a"))
            data.append(pack("FED-MINNEAPOLIS", title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-MINNEAPOLIS entry error: {e}")
    return data
