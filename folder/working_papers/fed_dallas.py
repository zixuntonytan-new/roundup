import re, io, time, requests, PyPDF2
from datetime import datetime
from .base import get_soup, pack, HEADERS

def scrape() -> list:
    s = get_soup("https://www.dallasfed.org/research/papers")
    data = []
    for year_id in [str(datetime.now().year), str(datetime.now().year - 1)]:
        try:
            container = s.find("div", {"class": "dal-tab__pane", "id": year_id})
            if not container:
                continue
            table = container.find("div", {"class": "dal-citations__inline--wp-index"})
            for el in table.find_all("div", class_="dal-index-item"):
                try:
                    title_tag = el.select_one("p.dal-headline > a")
                    title = title_tag.text.strip()
                    link = "https://www.dallasfed.org" + title_tag["href"]
                    author = el.select_one("p.dal-author").text.strip()
                    abstract_tag = el.select_one("div.dal-abstract > p")
                    abstract = abstract_tag.text.strip().replace("Abstract: ", "") if abstract_tag else ""
                    date = ""
                    pdf_tag = el.select_one("div.dal-abstract a[href$='.pdf']")
                    if pdf_tag:
                        try:
                            time.sleep(1)
                            pdf_bytes = requests.get(
                                "https://www.dallasfed.org" + pdf_tag["href"],
                                headers=HEADERS, timeout=30
                            ).content
                            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                            text = reader.pages[1].extract_text().replace("\n", " ")
                            m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)( \d{1,2},)? \d{4}", text)
                            date = m.group() if m else ""
                        except Exception:
                            pass
                    data.append(pack("FED-DALLAS", title, link, author, abstract, date))
                except Exception as e:
                    print(f"[WP] FED-DALLAS entry error: {e}")
        except Exception as e:
            print(f"[WP] FED-DALLAS year {year_id} error: {e}")
    return data
