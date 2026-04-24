import feedparser
from .base import get_soup, pack, HEADERS

def scrape() -> list:
    f = feedparser.parse("https://www.bankofengland.co.uk/rss/publications")
    if not f.entries:
        print("[WP] BOE: feed returned 0 entries")
        return []
    data = []
    for entry in f.entries:
        try:
            if "working paper" not in getattr(entry, "summary", "").lower():
                continue
            link = entry.link
            date = entry.published[:-14] if hasattr(entry, "published") else ""
            ls = get_soup(link)
            content_div = ls.find("div", {"class": "page-content"})
            abstract = ""
            author = ""
            if content_div:
                potential = []
                for tag in content_div.find_all(["p", "div"], recursive=False):
                    if tag.find("a", {"class": "btn btn-pubs btn-has-img btn-lg"}):
                        break
                    potential.append(tag.text.strip())
                abstract = max(potential, key=len) if potential else ""
                try:
                    author = content_div.text.strip().split("\n")[1].replace("By", "").strip()
                except Exception:
                    pass
            data.append(pack("BOE", entry.title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] BOE entry error: {e}")
    return data
