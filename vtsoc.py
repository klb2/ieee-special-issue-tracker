import re
import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

URL_SOC = "https://vtsociety.org"
JOURNALS = {
        "OJVT": "https://vtsociety.org/publication/ieee-ojvt/special-issues",
        "TVT": "https://vtsociety.org/publication/transactions-vehicular-technology/call-papers",
        }

#RE_DATE = r"Manuscript submission: (.+? \d{1,2}, \d{4})(?:.*)Final publication: (.+)"
RE_DATE = r"(?:.*)Deadline:(\d{1,2} \w+ \d{4})(?:.*)"


def get_all_cfp():
    data = []
    for journal, url in JOURNALS.items():
        data.append(parse_journal_cfp(url, journal))
    data = pd.concat(data, ignore_index=True)
    # data = translate_data_formats(data)
    return data

def parse_journal_cfp(url: str, journal: str):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    posts = soup("main")[0].find_all("article")
    rows = []
    for post in posts:
        topic_cell = post.find("h3").find("a")
        topic = unicodedata.normalize("NFKD", topic_cell.get_text(strip=True))
        try:
            url_cfp = f"{topic_cell['href']}"
            topic = f'<a href="{url_cfp}">{topic}</a>'
        except:
            url_cfp = ""
        pub_date = "Unknown"
        try:
            _match = re.match(RE_DATE, post.get_text(strip=True))
            due_date = _match.groups()[0]
        except:
            continue
        journal = f'<a href="{url}">{journal}</a>'
        rows.append([topic, due_date, pub_date, journal])
    #if not rows:
    #    raise ValueError("No entries found")
    data = pd.DataFrame(
        data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL]
    )
    return data


if __name__ == "__main__":
    data = get_all_cfp()
