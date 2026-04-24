from .base import get_soup, pack

def scrape() -> list:
    try:
        s = get_soup("https://bfi.uchicago.edu/working-papers/")
    except Exception as e:
        print(f"[WP] BFI fetch error: {e}")
        return []
    data = []
    for el in s.select("div.teaser.teaser--working-paper"):
        try:
            title_a = el.select_one("h2.teaser__title a")
            if not title_a:
                continue
            link = title_a["href"]
            title = title_a.text.strip()
            author_el = el.select_one("div.teaser__names")
            author = author_el.text.strip() if author_el else ""
            date_el = el.select_one("span.meta__date")
            date_str = date_el.text.strip() if date_el else ""
            ls = get_soup(link)
            abstract_el = ls.select_one("div.textblock")
            abstract = abstract_el.text.strip() if abstract_el else ""
            data.append(pack("BFI", title, link, author, abstract, date_str))
        except Exception as e:
            print(f"[WP] BFI entry error: {e}")
    return data
