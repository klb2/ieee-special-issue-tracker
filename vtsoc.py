import re
import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

URL = "https://vtsociety.org/publication/ieee-ojvt/special-issues"
URL_SOC = "https://vtsociety.org"

RE_TOPIC = r'Special (?:Issue|Series) on (.+)'
RE_DATE = r'Manuscript submission: (.+? \d{1,2}, \d{4})(?:.*)Final publication: (.+)'


def get_all_cfp():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    #posts = soup("table")[0].find_all("tr")
    posts = soup.find("div", attrs={"class": "block-views-blockmedia-call-documents-block-card-grid"})
    posts = posts.find_all("li")
    journal = "OJVT"
    rows = []
    for post in posts:
        title_cell = post.find("h3").find("a")
        topic = unicodedata.normalize("NFKD", title_cell.text)
        topic = re.match(RE_TOPIC, topic).groups()[0]
        try:
            url_cfp = title_cell['href']
            topic = f'<a href="{url_cfp}">{topic}</a>'
        except:
            url_cfp = ""
        date = post.find("time")
        due_date = date['datetime']
        due_date = due_date[:10]
        pub_date = "Unknown"
        journal = f'<a href="{URL}">{journal}</a>'
        rows.append([topic, due_date, pub_date, journal])
    if not rows:
        raise ValueError("No entries found")
    data = pd.DataFrame(data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL])
    return data

if __name__ == "__main__":
    data = get_all_cfp()
