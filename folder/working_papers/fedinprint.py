import requests
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from .base import pack, HEADERS

_FEEDS = {
    "FED-BOSTON":      "https://www.fedinprint.org/rss/boston.rss",
    "FED-KANSASCITY":  "https://www.fedinprint.org/rss/kansascity.rss",
    "FED-MINNEAPOLIS": "https://www.fedinprint.org/rss/minneapolis.rss",
    "FED-STLOUIS":     "https://www.fedinprint.org/rss/stlouis.rss",
}

def _parse_feed(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception:
        return feedparser.parse(url)

def scrape_bank(source_name: str, feed_url: str) -> list:
    feed = _parse_feed(feed_url)
    if not feed.entries:
        print(f"[WP] {source_name}: feed returned 0 entries")
        return []

    data = []
    for entry in feed.entries:
        try:
            series = getattr(entry, "bibo_series", "") or ""
            if "Working Paper" not in series:
                continue

            title = entry.title
            link = entry.link
            author = getattr(entry, "author", "")
            if hasattr(entry, "dc_creator"):
                author = entry.dc_creator

            abstract = BeautifulSoup(
                getattr(entry, "summary", ""), "html.parser"
            ).get_text().strip()

            date = ""
            if getattr(entry, "published_parsed", None):
                date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
            elif hasattr(entry, "dc_date"):
                date = entry.dc_date

            data.append(pack(source_name, title, link, author, abstract, date))
        except Exception as e:
            print(f"[WP] {source_name} entry error: {e}")

    return data


def scrape_boston()     -> list: return scrape_bank("FED-BOSTON",     _FEEDS["FED-BOSTON"])
def scrape_kansascity() -> list: return scrape_bank("FED-KANSASCITY",  _FEEDS["FED-KANSASCITY"])
def scrape_minneapolis()-> list: return scrape_bank("FED-MINNEAPOLIS", _FEEDS["FED-MINNEAPOLIS"])
def scrape_stlouis()    -> list: return scrape_bank("FED-STLOUIS",     _FEEDS["FED-STLOUIS"])
