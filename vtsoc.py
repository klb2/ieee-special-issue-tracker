import logging
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
    "VTM": "https://vtsociety.org/publication/vtmagazine#documents",
}

# RE_DATE = r"Manuscript submission: (.+? \d{1,2}, \d{4})(?:.*)Final publication: (.+)"
RE_DATE = r"(?:.*)Deadline:(\d{1,2} \w+ \d{4})(?:.*)"

LOGGER = logging.getLogger("vtsoc")


def get_all_cfp():
    data = []
    for journal, url in JOURNALS.items():
        data.append(parse_journal_cfp(url, journal))
    data = pd.concat(data, ignore_index=True)
    # data = translate_data_formats(data)
    return data


def parse_journal_cfp(url: str, journal: str):
    LOGGER.info(f"Parsing journal {journal}")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    LOGGER.debug(soup)
    if not resp.ok:
        raise requests.ConnectionError("Error while retrieving the CfP website.")
    posts = soup("main")[0].find_all("article")
    rows = []
    for post in posts:
        try:
            topic_cell = post.find("h3").find("a")
        except AttributeError:
            break
            # return
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
        journal_url = f'<a href="{url}">{journal}</a>'
        rows.append([topic, due_date, pub_date, journal_url])
    # if not rows:
    #    raise ValueError("No entries found")
    data = pd.DataFrame(
        data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL]
    )
    return data


if __name__ == "__main__":
    data = get_all_cfp()
    print(data)
