import re
import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

URL = "https://vtsociety.org/publication/ieee-ojvt/special-issues"
URL_SOC = "https://vtsociety.org"

RE_DATE = r'Manuscript submission: (.+? \d{1,2}, \d{4})(?:.*)Final publication: (.+)'


def get_all_cfp():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    posts = soup("table")[0].find_all("tr")
    journal = "OJVT"
    rows = []
    for post in posts:
        cells = post.find_all("td")
        topic = unicodedata.normalize("NFKD", cells[0].text)
        try:
            url_cfp = f"{URL_SOC}{cells[1].find('a')['href']}"
            topic = f'<a href="{url_cfp}">{topic}</a>'
        except:
            url_cfp = ""
        date_string = cells[2].text
        date_string = unicodedata.normalize("NFKD", date_string)
        try:
            due_date, pub_date = re.match(RE_DATE, date_string).groups()
        except:
            continue
        journal = f'<a href="{URL}">{journal}</a>'
        rows.append([topic, due_date, pub_date, journal])
    if not rows:
        raise ValueError("No entries found")
    data = pd.DataFrame(data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL])
    return data

if __name__ == "__main__":
    data = get_all_cfp()
