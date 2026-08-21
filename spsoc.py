import logging
import re
import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC

LOGGER = logging.getLogger("spsoc")

# URL = "https://signalprocessingsociety.org/publications-resources/special-issue-deadlines"
URL = "https://signalprocessingsociety.org/publications-resources/special-issue-deadlines?page={}"
# URL = "https://signalprocessingsociety.org/publications-resources/special-issue-deadlines?tid=All&sort_by=field_date_value&sort_order=ASC&page={}"
URL_SOC = "https://signalprocessingsociety.org"

RE_POST_HEADER = (
    r"(?:Call for Papers:\s)?(?:(IEEE .+) Special (?:Issue|Series|Section) on )?(.+)"
)
RE_DATE = r".+:\s((?:\d{1,2} )?\w+\s(?:\d{1,2}, )?\d{4}|\d{1,2}-\w+-\d{4})"


def get_all_cfp():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    page_items = soup.find_all("li", {"class": "pager-item"})
    num_pages = len(page_items) + 1
    rows = []
    for page in range(num_pages):
        _page_rows = get_single_page(page)
        rows.append(_page_rows)
    rows = pd.concat(rows)
    return rows


def get_single_page(page=0):
    LOGGER.debug(f"Working on page {page:d}")
    url = URL.format(page)
    resp = requests.get(url)
    if not resp.ok:
        raise requests.ConnectionError("Error while retrieving the CfP website.")
    soup = BeautifulSoup(resp.text, "html.parser")
    posts = soup.find_all("article", {"class": "node"})
    LOGGER.debug(f"Found {len(posts):d} open calls")
    rows = []
    for post in posts:
        header = post.find("h4")  # .text.strip()
        header_text = header.text.strip()
        LOGGER.debug(f"Title: {header_text}")
        journal, topic = re.match(RE_POST_HEADER, header_text).groups()
        LOGGER.debug(f"Topic: {topic}")
        LOGGER.debug(f"Journal: {journal}")
        if journal is None:
            journal = "Unknown"
        journal = f'<a href="{URL}">{journal}</a>'
        body = post.find("p")
        for _match in body.find_all("strong"):
            _match.unwrap()
        body.smooth()
        _date_strings = [re.sub(r"\s", " ", k) for k in body.stripped_strings]
        due_date = re.match(RE_DATE, str(_date_strings[0]))[1]
        LOGGER.debug(f"Due date: {due_date}")
        try:
            pub_date = re.match(RE_DATE, str(_date_strings[1]))[1]
        except:  # TypeError:
            pub_date = "Unknown"
        LOGGER.debug(f"Publication date: {pub_date}")
        try:
            url_cfp = f"{URL_SOC}{header.find('a')['href']}"
            topic = f'<a href="{url_cfp}">{topic}</a>'
        except:
            try:
                url_cfp = f"{URL_SOC}{header.find('a')['href']}"
                topic = f'<a href="{url_cfp}">{topic}</a>'
            except:
                url_cfp = ""
        rows.append([topic, due_date, pub_date, journal])
    # if not rows:
    #    raise ValueError("No entries found")
    data = pd.DataFrame(
        data=rows, columns=[COL_TOPIC, COL_DEADLINE, COL_PUB_DATE, COL_JOURNAL]
    )
    return data


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s")
    LOGGER.setLevel(logging.DEBUG)
    data = get_all_cfp()
    print(data)
