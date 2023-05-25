import re
import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

URL = "https://signalprocessingsociety.org/publications-resources/special-issue-deadlines"
#URL = "https://signalprocessingsociety.org/publications-resources/special-issue-deadlines?tid=All&sort_by=field_date_value&sort_order=ASC&page={}"
URL_SOC = "https://signalprocessingsociety.org"

RE_POST_HEADER = r'(IEEE .+) Special (?:Issue|Series) on (.+)'
RE_DATE = r'.+: ((?:\d{1,2} )?\w+ (?:\d{1,2}, )?\d{4})'


def get_all_cfp():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    #posts = soup.find_all("section", "post-content")
    _content = soup.find("div", {"class": "content"})
    _table = soup.find("table")
    _table = _table.find("tbody")
    posts = _table.find_all("tr")
    rows = []
    for post in posts:
        _cells = post.find_all("td")
        _info = _cells[0]
        header = _info.find("h4")#.text.strip()
        header_text = header.text.strip()
        journal, topic = re.match(RE_POST_HEADER, header_text).groups()
        journal = f'<a href="{URL}">{journal}</a>'
        body = post.find("p")
        _date_strings = list(body.stripped_strings)
        due_date = re.match(RE_DATE, str(_date_strings[0]))[1]
        try:
            pub_date = re.match(RE_DATE, str(_date_strings[1]))[1]
        except: #TypeError:
            pub_date = "Unknown"
        try:
            url_cfp = f"{URL_SOC}{body.find('a')['href']}"
            topic = f'<a href="{url_cfp}">{topic}</a>'
        except:
            try:
                url_cfp = f"{URL_SOC}{header.find('a')['href']}"
                topic = f'<a href="{url_cfp}">{topic}</a>'
            except:
                url_cfp = ""
        rows.append([topic, due_date, pub_date, journal])
    if not rows:
        raise ValueError("No entries found")
    data = pd.DataFrame(data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL])
    return data

if __name__ == "__main__":
    data = get_all_cfp()
