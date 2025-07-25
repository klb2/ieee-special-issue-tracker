import re
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

LOGGER = logging.getLogger("itsoc")

URL = "https://www.itsoc.org/jsait/calls-for-papers"
URL_SOC = "https://www.itsoc.org"

RE_ENTRY_TITLE = r"(?:CFP: )?(.+?)\s?(?:(\(Closed\)|\(Currently Open\))|$)"
RE_DATE = r"Deadline:\s+((?:\d{1,2} )?\w+ (?:\d{1,2}, )?\d{4})"


def get_all_cfp():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }
    resp = requests.get(URL, headers=headers)
    LOGGER.debug(f"Response code: {resp.status_code}")
    soup = BeautifulSoup(resp.text, "html.parser")
    LOGGER.debug(soup)
    if not resp.ok:
        raise requests.ConnectionError("Error while retrieving the CfP website.")
    entries = soup.find_all("div", {"class": "call-for-papers"})
    LOGGER.debug(f"Found a total of {len(entries):d} entries")
    rows = []
    journal = f'<a href="{URL}">JSAIT</a>'
    for entry in entries:
        if "call-for-papers--closed" in entry["class"]:
            continue
        title_div = entry.find("div", {"class": "call-for-papers__title"})
        _topic = title_div.get_text(strip=True)
        topic = re.match(RE_ENTRY_TITLE, _topic)[1]
        url_cfp = title_div.find("a")["href"]
        url_cfp = f"{URL_SOC}{url_cfp}"
        topic = f'<a href="{url_cfp}">{topic}</a>'

        try:
            date_div = entry.find("div", {"class": "call-for-papers__date"})
            _date = date_div.get_text(strip=True)
            due_date = re.match(RE_DATE, _date)[1]
        except:
            continue
        pub_date = "Unknown"
        rows.append([topic, due_date, pub_date, journal])
    # if not rows:
    #    raise ValueError("No entries found")
    data = pd.DataFrame(
        data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL]
    )
    return data


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - [%(levelname)8s] %(name)s: %(message)s",
        level=logging.DEBUG,
    )
    data = get_all_cfp()
    print(data)
