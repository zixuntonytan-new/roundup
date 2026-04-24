import re
import feedparser
from ..generic_scraper import GenericScraper


class BISScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="BIS")

    def fetch_data(self):
        url = (
            "https://www.bis.org/doclist/wppubls.rss?from=&till=&objid=wppubls"
            "&page=&paging_length=10&sort_list=date_desc&theme=wppubls"
            "&ml=false&mlurl=&emptylisttext="
        )
        f = feedparser.parse(url)

        data = []
        for entry in f.entries:
            try:
                # Use regex to split on any <br> variant the feed may use
                parts = re.split(r"<br\s*/?>", entry.description, maxsplit=1)
                abstract = parts[1].strip() if len(parts) > 1 else ""
                author = (
                    re.sub(r"^by\s*", "", parts[0], flags=re.IGNORECASE).strip()
                    if parts else ""
                )
                date = entry.date.split("T")[0] if hasattr(entry, "date") else ""
                number = (
                    entry.link
                    .replace("https://www.bis.org/publ/work", "")
                    .replace(".htm", "")
                )
                data.append({
                    "Title": entry.title,
                    "Link": entry.link,
                    "Date": date,
                    "Abstract": abstract,
                    "Author": author,
                    "Number": number,
                })
            except Exception as e:
                print(f"[BIS] entry error: {e}")

        return data
