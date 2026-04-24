import re, feedparser
from .base import pack

def scrape() -> list:
    url = "https://www.bis.org/doclist/wppubls.rss?from=&till=&objid=wppubls&page=&paging_length=10&sort_list=date_desc&theme=wppubls&ml=false&mlurl=&emptylisttext="
    f = feedparser.parse(url)
    data = []
    for entry in f.entries:
        try:
            parts = re.split(r'<br\s*/?>', entry.description, maxsplit=1)
            abstract = parts[1].strip() if len(parts) > 1 else ""
            author = re.sub(r'^by\s*', '', parts[0], flags=re.IGNORECASE).strip() if parts else ""
            date = entry.date.split("T")[0] if hasattr(entry, "date") else ""
            data.append(pack("BIS", entry.title, entry.link, author, abstract, date))
        except Exception as e:
            print(f"[WP] BIS entry error: {e}")
    return data
