import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import COL_JOURNAL, COL_DEADLINE, COL_PUB_DATE, COL_TOPIC
from others import _iotj_cfp


URL_SOC = "https://www.comsoc.org"
JOURNALS = {
    "JSAC": "https://www.comsoc.org/publications/journals/ieee-jsac/cfp",
    "TCCN": "https://www.comsoc.org/publications/journals/ieee-tccn/cfp",
    "OJCOMS": "https://www.comsoc.org/publications/journals/ieee-ojcoms/cfp",
    "TGCN": "https://www.comsoc.org/publications/journals/ieee-tgcn/cfp",
    "TMBMC": "https://www.comsoc.org/publications/journals/ieee-tmbmc/cfp",
    "TNSE": "https://www.comsoc.org/publications/journals/ieee-tnse/cfp",
    "TNSM": "https://www.comsoc.org/publications/journals/ieee-tnsm/cfp",
}
SPECIAL_JOURNALS = {
    "IOTJ": _iotj_cfp,
}

_COL_DEADLINE = "Manuscript Submission Deadline"
_COL_PUB_DATE = "Publication Date"
_COL_TOPIC = "Paper Topic"


def parse_comsoc_cfp(url: str, journal_name: str):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")
    table = tables[0]
    header = table.findChildren("th")
    columns = [th.text.strip() for th in header]
    body = table.findChild("tbody")
    rows = body.find_all("tr")
    # content_rows = [list(_row.stripped_strings) for _row in rows]
    content_rows = []
    for post in rows:
        cells = post.find_all("td")
        topic = unicodedata.normalize("NFKD", cells[0].text).strip()
        try:
            url_cfp = f"{URL_SOC}{cells[0].find('a')['href']}"
            topic = f'<a href="{url_cfp}">{topic}</a>'
        except:
            url_cfp = ""
        pub_date = unicodedata.normalize("NFKD", cells[1].text).strip()
        due_date = unicodedata.normalize("NFKD", cells[2].text).strip()
        content_rows.append([topic, pub_date, due_date])
    data = pd.DataFrame(data=content_rows, columns=columns)
    data[COL_JOURNAL] = f'<a href="{url}">{journal_name}</a>'
    data = translate_data_formats(data)
    return data


def translate_data_formats(data: pd.DataFrame):
    data = data.rename(
        columns={
            _COL_DEADLINE: COL_DEADLINE,
            _COL_PUB_DATE: COL_PUB_DATE,
            _COL_TOPIC: COL_TOPIC,
        }
    )
    return data


def get_all_cfp():
    data = []
    for journal, url in JOURNALS.items():
        data.append(parse_comsoc_cfp(url, journal))
    for journal, func in SPECIAL_JOURNALS.items():
        data.append(func(journal=journal))
    data = pd.concat(data, ignore_index=True)
    # data = translate_data_formats(data)
    return data


if __name__ == "__main__":
    data = get_all_cfp()
    print(data)
