import requests, feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from .base import pack, HEADERS

def _parse_feed(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception:
        return feedparser.parse(url)

def scrape() -> list:
    feed = _parse_feed("https://research.stlouisfed.org/rss/wp/")
    if not feed.entries:
        feed = _parse_feed("https://www.fedinprint.org/feeds/stls.rss")
    if not feed.entries:
        print("[WP] FED-STLOUIS: feed returned 0 entries")
        return []
    data = []
    for entry in feed.entries:
        try:
            title = entry.title
            link = entry.link
            date = ""
            if getattr(entry, "published_parsed", None):
                date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
            author = getattr(entry, "author", "")
            abstract = BeautifulSoup(getattr(entry, "summary", ""), "html.parser").get_text().strip()
            data.append(pack("FED-STLOUIS", title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] FED-STLOUIS entry error: {e}")
    return data
