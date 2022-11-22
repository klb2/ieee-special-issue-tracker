import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

#URL = "https://signalprocessingsociety.org/publications-resources/special-issue-deadlines"
URL = "https://signalprocessingsociety.org/publications-resources/special-issue-deadlines?tid=All&sort_by=field_date_value&sort_order=ASC&page={}"

RE_POST_HEADER = r'(IEEE .+) Special Issue on (.+)'
RE_DATE = r'.+: ((?:\d{1,2} )?\w+ (?:\d{1,2}, )?\d{4})'


def get_all_cfp():
    data = []
    number = 0
    while True:
        try:
            page_data = get_cfp_single_page(number)
            data.append(page_data)
        except ValueError:
            break
        number = number + 1
    data = pd.concat(data, ignore_index=True)
    return data

def get_cfp_single_page(number: int):
    url = URL.format(number)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    posts = soup.find_all("section", "post-content")
    rows = []
    for post in posts:
        header = post.find("header").find("h2").text.strip()
        journal, topic = re.match(RE_POST_HEADER, header).groups()
        body = post.find("p")
        _date_strings = list(body.stripped_strings)
        due_date = re.match(RE_DATE, str(_date_strings[0]))[1]
        try:
            pub_date = re.match(RE_DATE, str(_date_strings[1]))[1]
        except TypeError:
            pub_date = "Unknown"
        rows.append([topic, due_date, pub_date, journal])
    if not rows:
        raise ValueError("No entries found")
    data = pd.DataFrame(data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL])
    return data

if __name__ == "__main__":
    data = get_all_cfp()
