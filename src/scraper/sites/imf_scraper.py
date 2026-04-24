"""
IMF Working Papers scraper.

Uses the Firecrawl API to render the JS-heavy IMF publications search page.
Requires FIRECRAWL_API_KEY to be set as an environment variable (GitHub secret
in CI, .env file locally).

If the API key is absent the scraper raises an exception and is marked offline.
"""
import os
import re
from ..generic_scraper import GenericScraper

_URL = "https://www.imf.org/en/publications/search?when=After&series=IMF+Working+Papers#cf-type=WRKNGPPRS"
_MAX = 20
_MONTHS = (
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
)


class IMFScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="IMF")

    def fetch_data(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise Exception("FIRECRAWL_API_KEY not set — IMF scraper skipped")

        from firecrawl import V1FirecrawlApp

        app = V1FirecrawlApp(api_key=api_key)
        result = app.scrape_url(_URL, formats=["markdown"], wait_for=3000)
        md = result.markdown or ""

        if not md:
            raise Exception("Firecrawl returned empty markdown for IMF")

        return self._parse(md)

    def _parse(self, md: str) -> list:
        """
        Parse Firecrawl markdown. Each block looks like:

          ### [Title](url)

          April 10, 2026

          Author A; Author BAbstract text here...

          Working Papers
        """
        data = []
        blocks = re.split(r"\n(?=#{1,4} \[)", md)

        for block in blocks[:_MAX]:
            try:
                m = re.search(r"#{1,4} \[(.+?)\]\((https?://[^\)]+)\)", block)
                if not m:
                    continue
                title = m.group(1).strip()
                url = m.group(2).strip()
                if "/publications/wp/" not in url.lower():
                    continue

                date_m = re.search(
                    rf"{_MONTHS}\s+\d{{1,2}},\s+\d{{4}}|\d{{4}}-\d{{2}}-\d{{2}}",
                    block,
                )
                date = date_m.group(0).strip() if date_m else ""

                # First non-heading, non-date, non-label content line is author+abstract blob
                blob = ""
                for line in block.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if re.match(r"#{1,4} ", line):
                        continue
                    if re.match(rf"{_MONTHS}\s+\d", line) or re.match(
                        r"\d{4}-\d{2}-\d{2}", line
                    ):
                        continue
                    if re.match(r"Working Papers?$", line, re.IGNORECASE):
                        continue
                    blob = line
                    break

                # Split authors from abstract at the last semicolon followed by a
                # lowercase→uppercase boundary (end of last author name)
                author, abstract = "", blob
                last_semi = blob.rfind(";")
                if last_semi >= 0:
                    tail = blob[last_semi:]
                    boundary = re.search(r"[a-z]([A-Z])", tail)
                    if boundary:
                        cut = last_semi + boundary.start(1)
                        author = blob[:cut].strip()
                        abstract = blob[cut:].strip()

                abstract = re.sub(
                    r"\s*Results per page.*$", "", abstract, flags=re.IGNORECASE
                ).strip()

                # Number: last path segment of URL (unique per paper)
                number = url.rstrip("/").split("/")[-1]

                if title:
                    data.append({
                        "Title": title,
                        "Author": author,
                        "Link": url,
                        "Abstract": abstract,
                        "Number": number,
                        "Date": date,
                    })
            except Exception as e:
                print(f"[IMF] entry error: {e}")

        if not data:
            raise Exception("IMF: parsed markdown but found no working paper entries")

        return data
