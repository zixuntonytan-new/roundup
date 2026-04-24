"""
IMF Working Papers scraper — uses Firecrawl to render the JS-heavy
publications search page with the working papers filter applied.

Token rotation: if results dry up, check the URL still resolves correctly
in a browser. The filter is applied via URL hash so no API credentials needed.

If Firecrawl API key rotates, update FIRECRAWL_API_KEY in .env.
"""

import os
import re
from firecrawl import Firecrawl
from .base import pack

_URL = "https://www.imf.org/en/publications/search?when=After&series=IMF+Working+Papers#cf-type=WRKNGPPRS"
_MAX = 20


def scrape() -> list:
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("[WP] IMF: FIRECRAWL_API_KEY not set")
        return []

    try:
        app = Firecrawl(api_key=api_key)
        result = app.scrape(
            _URL,
            formats=["markdown"],
            wait_for=3000,
        )
        md = result.markdown if hasattr(result, "markdown") else (result.get("markdown") or "")
    except Exception as e:
        print(f"[WP] IMF fetch error: {e}")
        return []

    if not md:
        print("[WP] IMF: Firecrawl returned empty markdown")
        return []

    return _parse(md)


_MONTHS = (r'(?:January|February|March|April|May|June|July|August|'
           r'September|October|November|December)')

def _parse(md: str) -> list:
    """
    Actual Firecrawl markdown structure per block:

      ### [Title](url)

      April 10, 2026

      Alex Pienkowski; Valentina Semenova; Ian C. Stuart; Yuntian LuAbstract text...

      Working Papers

    Authors and abstract are concatenated on one line with no separator.
    Split on the first [lowercase][Uppercase] boundary after a semicolon-delimited name.
    """
    data = []
    blocks = re.split(r'\n(?=#{1,4} \[)', md)

    for block in blocks[:_MAX]:
        try:
            # Title + URL
            m = re.search(r'#{1,4} \[(.+?)\]\((https?://[^\)]+)\)', block)
            if not m:
                continue
            title = m.group(1).strip()
            url   = m.group(2).strip()
            if "/publications/wp/" not in url.lower():
                continue

            # Date — own line, e.g. "April 10, 2026"
            date_m = re.search(rf'{_MONTHS}\s+\d{{1,2}},\s+\d{{4}}|\d{{4}}-\d{{2}}-\d{{2}}', block)
            date = date_m.group(0).strip() if date_m else ""

            # Find the author+abstract blob — the long line that isn't the heading or date
            blob = ""
            for line in block.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if re.match(r'#{1,4} ', line):
                    continue
                if re.match(rf'{_MONTHS}\s+\d', line) or re.match(r'\d{{4}}-\d{{2}}-\d{{2}}', line):
                    continue
                if re.match(r'Working Papers?$', line, re.IGNORECASE):
                    continue
                blob = line
                break  # first content line is the author+abstract blob

            # Split authors from abstract: find last semicolon, then first
            # [lowercase][Uppercase] boundary in the tail — that's where the
            # last author name ends and the abstract begins.
            authors, abstract = "", blob
            last_semi = blob.rfind(';')
            if last_semi >= 0:
                tail = blob[last_semi:]
                boundary = re.search(r'[a-z]([A-Z])', tail)
                if boundary:
                    cut = last_semi + boundary.start(1)
                    authors  = blob[:cut].strip()
                    abstract = blob[cut:].strip()

            abstract = re.sub(r'\s*Results per page.*$', '', abstract, flags=re.IGNORECASE).strip()

            if title:
                data.append(pack("IMF", title, url, authors, abstract, date))
        except Exception as e:
            print(f"[WP] IMF entry error: {e}")

    if not data:
        print("[WP] IMF: parsed markdown but found no working paper entries")
    return data
