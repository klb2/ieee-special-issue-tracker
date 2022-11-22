import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

URL = "https://www.itsoc.org/jsait/calls-for-papers"

RE_ENTRY_TITLE = r'(?:CFP: )?(.+) (?:(\(Closed\)|\(Currently Open\)))'
RE_DATE = r'.+ ((?:\d{1,2} )?\w+ (?:\d{1,2}, )?\d{4})'

def get_all_cfp():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    entries = soup.find_all("div", "content--teaser--card")
    rows = []
    journal = f'<a href="{URL}">JSAIT</a>'
    for entry in entries:
        _strings = list(entry.stripped_strings)
        if len(_strings) < 4:
            continue
        topic = re.match(RE_ENTRY_TITLE, str(_strings[0]))[1]
        #description = _strings[1]
        try:
            due_date = re.match(RE_DATE, str(_strings[-2]))[1]
        except:
            continue
        pub_date = "Unknown"
        rows.append([topic, due_date, pub_date, journal])
    if not rows:
        raise ValueError("No entries found")
    data = pd.DataFrame(data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL])
    return data

if __name__ == "__main__":
    entries = get_all_cfp()
