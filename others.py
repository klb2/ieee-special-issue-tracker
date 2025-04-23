import unicodedata
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC


RE_TOPIC = r"(?:Special (?:Issue|issue) on )?(.+)"
RE_DATE = r"Submission Deadline: (\w+ (?:\d{1,2}\w+, )?\d{4})"


def _iotj_cfp(journal="IOTJ"):
    url = "https://ieee-iotj.org/special-issues/"
    journal = f'<a href="{url}">{journal}</a>'
    rows = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    div = soup.find("div", id="usi1")
    posts = div.find_all("li")
    for post in posts:
        title_link = post.find("a")
        _topic = unicodedata.normalize("NFKD", title_link.text)
        topic = re.match(RE_TOPIC, _topic).groups()[0]
        try:
            url_cfp = title_link["href"]
            topic = f'<a href="{url_cfp}">{topic}</a>'
        except:
            url_cfp = ""
        date_string = post.text
        date_string = unicodedata.normalize("NFKD", date_string)
        try:
            due_date = re.search(RE_DATE, date_string).groups()[0]
        except:
            continue
        pub_date = "Unknown"
        rows.append([topic, due_date, pub_date, journal])
    data = pd.DataFrame(
        data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL]
    )
    return data


if __name__ == "__main__":
    data = _iotj_cfp()
    print(data)
