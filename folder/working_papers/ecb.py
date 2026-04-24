from .base import get_soup_js, pack

def scrape() -> list:
    url = "https://www.ecb.europa.eu/pub/research/working-papers/html/index.en.html"
    try:
        # wait for dt[isodate] to confirm lazy-loaded content is present
        soup = get_soup_js(url, wait_css="dt[isodate]")
    except Exception as e:
        print(f"[WP] ECB fetch error: {e}")
        return []

    elements = soup.find("dl", {"class": "ecb-basicList"})
    if not elements:
        print("[WP] ECB: could not find paper list")
        return []

    filtered_dt = [dt for dt in elements.find_all("dt") if dt.has_attr("isodate")]
    data = []
    for dt in filtered_dt[:20]:
        dd = dt.find_next_sibling("dd")
        if not dd:
            continue
        try:
            date_div = dt.find("div", class_="date")
            date = date_div.text.strip() if date_div else ""

            title_div = dd.find("div", class_="title")
            title = title_div.text.strip() if title_div else "No title"

            author_list = dd.find_all("li")
            authors = ", ".join(li.text.strip() for li in author_list) if author_list else ""

            abstract_marker = dd.find("dt", string="Abstract")
            abstract = abstract_marker.find_next_sibling("dd").text.strip() if abstract_marker else ""

            link = ""
            if title_div:
                a = title_div.find("a")
                if a and a.get("href"):
                    link = "https://www.ecb.europa.eu" + a["href"]

            data.append(pack("ECB", title, link, authors, abstract, date))
        except Exception as e:
            print(f"[WP] ECB entry error: {e}")
    return data
