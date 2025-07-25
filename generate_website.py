import os.path
from datetime import datetime
import logging

import pandas as pd
import jinja2

import comsoc
import spsoc
import itsoc
import vtsoc

from constants import COL_DEADLINE, COL_TOPIC, COL_JOURNAL, COL_PUB_DATE

LOGGER = logging.getLogger("main")

FORMATTER_DATE = lambda x: datetime.strftime(x, "%B %d, %Y")
FORMATTER_UNESCAPE = lambda x: x.replace("&gt;", ">").replace("&lt;", "<")

SOCIETIES = [
    {
        "name": "Communications Society",
        "id": "comsoc",
        "url": "https://www.comsoc.org/",
        "module": comsoc,
    },
    {
        "name": "Signal Processing Society",
        "id": "spsoc",
        "url": "https://signalprocessingsociety.org/",
        "module": spsoc,
    },
    {
        "name": "Information Theory Society",
        "id": "itsoc",
        "url": "https://www.itsoc.org/",
        "module": itsoc,
    },
    {
        "name": "Vehicular Technology Society",
        "id": "vtsoc",
        "url": "https://vtsociety.org/",
        "module": vtsoc,
    },
]


def clean_dataframe(data):
    deadlines = pd.to_datetime(data[COL_DEADLINE], format="mixed", errors="coerce")
    data[COL_DEADLINE] = deadlines
    data = data.dropna()
    data = data[data[COL_DEADLINE] >= datetime.today()]
    return data


def generate_society_table(module, **kwargs):
    data = module.get_all_cfp()
    LOGGER.info(f"Found a total of {len(data):d} entries.")
    data = clean_dataframe(data)
    LOGGER.info(f"Number of active calls: {len(data):d}")
    data = data.sort_values(COL_DEADLINE)
    data = data[[COL_TOPIC, COL_DEADLINE, COL_JOURNAL, COL_PUB_DATE]]
    if data.empty:
        return "No open call for papers"
    html_table = data.to_html(
        index=False,
        border=False,
        justify="unset",
        escape=False,
        formatters={COL_DEADLINE: FORMATTER_DATE},
    )
    return html_table


def main():
    for soc_info in SOCIETIES:
        LOGGER.info("Working on society: {name}".format(**soc_info))
        try:
            _table = generate_society_table(**soc_info)
        except Exception as e:
            LOGGER.error(f"Error while generating the table for society '{name}'")
            LOGGER.error(e)
            _table = "Error while parsing the calls for papers"
        soc_info["table"] = _table

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("index.html")
    timestamp = datetime.now().strftime("%B %d, %Y")
    content = template.render(societies=SOCIETIES, timestamp=timestamp)
    out_path = os.path.join("public", "index.html")
    with open(out_path, "w") as html_file:
        html_file.write(content)
    # return data


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - [%(levelname)8s] %(name)s: %(message)s",
        level=logging.DEBUG,
    )
    data = main()
