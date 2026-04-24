from .base import get_soup, pack

def scrape() -> list:
    s = get_soup("https://www.bea.gov/research/papers")
    data = []
    seen = set()
    for el in s.select("div.view-content div.card"):
        try:
            raw_href = el.find("h2", {"class": "paper-title"}).find("a")["href"]
            # strip leading slash if present to avoid double-slash, then strip trailing slash for consistency
            landing_url = "https://www.bea.gov/" + raw_href.lstrip("/")
            landing_url = landing_url.rstrip("/")
            if landing_url in seen:
                continue
            seen.add(landing_url)
            ls = get_soup(landing_url)
            number_url = ls.find("h2", class_="card-title").find("a")["href"]
            if "BEA-WP" not in number_url:
                continue
            abstract = ls.find("p", {"class": "card-abstract"}).get_text(strip=True)
            title = el.find("h2", {"class": "paper-title"}).text.strip()
            author = el.find("div", {"class": "paper-mod-date"}).text.strip()
            date = el.find("time").get("datetime", "").split("T")[0]
            data.append(pack("BEA", title, landing_url, author, abstract, date))
        except Exception as e:
            print(f"[WP] BEA entry error: {e}")
    return data
