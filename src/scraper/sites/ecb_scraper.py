import re
from ..generic_scraper import GenericScraper
from src.scraper.external_requests import selenium_soup


class ECBScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="ECB")

    def fetch_data(self):
        url = "https://www.ecb.europa.eu/pub/research/working-papers/html/index.en.html"
        soup = selenium_soup(url=url, wait_css="dt[isodate]")

        elements = soup.find("dl", {"class": "ecb-basicList"})
        if not elements:
            raise Exception("ECB: could not find paper list")

        filtered_dt = [dt for dt in elements.find_all("dt") if dt.has_attr("isodate")]
        data = []
        for dt in filtered_dt[:20]:
            dd = dt.find_next_sibling("dd")
            if not dd:
                continue

            date_div = dt.find("div", class_="date")
            date = date_div.text.strip() if date_div else ""

            title_div = dd.find("div", class_="title")
            title = title_div.text.strip() if title_div else "No title"

            author_list = dd.find_all("li")
            author = ", ".join(li.text.strip() for li in author_list) if author_list else ""

            abstract_marker = dd.find("dt", string="Abstract")
            abstract = (
                abstract_marker.find_next_sibling("dd").text.strip()
                if abstract_marker
                else ""
            )

            link = ""
            if title_div:
                a = title_div.find("a")
                if a and a.get("href"):
                    link = "https://www.ecb.europa.eu" + a["href"]

            # Extract paper number from URL pattern ecb.wp{NUMBER}~...
            m = re.search(r"ecb\.wp(\w+)", link)
            if m:
                number = m.group(1).split("~")[0]
            else:
                number = re.sub(r"\W", "", link.split("/")[-1])[:20]

            data.append({
                "Title": title,
                "Author": author,
                "Link": link,
                "Abstract": abstract,
                "Number": number,
                "Date": date,
            })

        return data
