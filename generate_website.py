import os.path
from datetime import datetime

import pandas as pd
import jinja2

import comsoc
import spsoc

from constants import COL_DEADLINE, COL_TOPIC, COL_JOURNAL, COL_PUB_DATE

FORMATTER_DATE = lambda x: datetime.strftime(x, "%B %d, %Y")

SOCIETIES = [
        {"name": "Communications Society",
         "id": "comsoc",
         "url": "https://www.comsoc.org/",
         "module": comsoc,
        },
        {"name": "Signal Processing Society",
         "id": "spsoc",
         "url": "https://signalprocessingsociety.org/",
         "module": spsoc,
        },
        ]

def clean_dataframe(data):
    deadlines = pd.to_datetime(data[COL_DEADLINE], errors='coerce')
    data[COL_DEADLINE] = deadlines
    data = data.dropna()
    return data

def generate_society_table(module, **kwargs):
    data = module.get_all_cfp()
    data = clean_dataframe(data)
    data = data.sort_values(COL_DEADLINE)
    data = data[[COL_TOPIC, COL_DEADLINE, COL_JOURNAL, COL_PUB_DATE]]
    html_table = data.to_html(index=False, border=False, justify='unset',
                              formatters={COL_DEADLINE: FORMATTER_DATE})
    return html_table

def main():
    for soc_info in SOCIETIES:
        print("Working on society: {name}".format(**soc_info))
        _table = generate_society_table(**soc_info)
        soc_info['table'] = _table

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("index.html")
    content = template.render(societies=SOCIETIES)
    out_path = os.path.join("public", "index.html")
    with open(out_path, 'w') as html_file:
        html_file.write(content)
    #return data

if __name__ == "__main__":
    data = main()