import json, time
from html import unescape
from .base import get_soup, pack

def scrape() -> list:
    s = get_soup("https://www.philadelphiafed.org/search-results/all-work?searchtype=working-papers")
    json_element = None
    for script in s.find_all("script"):
        if "Working Paper" in script.get_text():
            json_element = script
            break
    if not json_element:
        print("[WP] FED-PHILADELPHIA: could not find JSON data block")
        return []
    try:
        json_str = json_element.string.split("data: ")[1].split("})")[0].strip()[:-1]
        json_data = json.loads(json_str)
    except Exception as e:
        print(f"[WP] FED-PHILADELPHIA JSON parse error: {e}")
        return []
    data = []
    for wp in json_data["results"]:
        try:
            title = unescape(wp["attributes"]["title"])
            author = ", ".join(a["name"] for a in wp["attributes"]["authors"])
            link = "https://www.philadelphiafed.org" + wp["attributes"]["url"]
            time.sleep(1)
            ls = get_soup(link)
            abstract_el = ls.find("div", {"class": "article-body"})
            abstract = " ".join(p.text for p in abstract_el.find_all("p")).strip().replace("\n", "") if abstract_el else ""
            date_el = ls.find("p", {"class": "article-date-published"})
            date = date_el.text.strip() if date_el else ""
            data.append(pack("FED-PHILADELPHIA", title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-PHILADELPHIA entry error: {e}")
    return data
