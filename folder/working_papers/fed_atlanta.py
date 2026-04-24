import feedparser
from datetime import datetime
from .base import pack

def scrape() -> list:
    f = feedparser.parse("https://www.atlantafed.org/rss/wps")
    data = []
    for entry in f.entries:
        try:
            if not getattr(entry, "published_parsed", None):
                continue
            dt = datetime(*entry.published_parsed[:6])
            date_str = dt.strftime("%Y-%m-%d")
            month_year = dt.strftime("%B") + " " + dt.strftime("%Y")
            if month_year in entry.description:
                abstract = entry.description.split(month_year)[1].strip()
            else:
                abstract = ""
            author = entry.description.split("Working Paper")[0].strip()
            data.append(pack("FED-ATLANTA", entry.title, entry.link, author, abstract, date_str))
        except Exception as e:
            print(f"[WP] FED-ATLANTA entry error: {e}")
    return data
