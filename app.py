from collections import Counter
from datetime import datetime
from itertools import cycle, islice
from math import ceil
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, abort

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
TABLE = os.environ["TABLE"]
COLUMN = os.environ["COLUMN"]
TEMPLATE_FOLDER = "templates"
DEFAULT_TEMPLATE = "line"

engine = create_engine(DATABASE_URL)
session = sessionmaker(engine)()

metadata = MetaData()
metadata.reflect(engine, only=[TABLE])

Base = automap_base(metadata=metadata)
Base.prepare()

SA_TABLE = getattr(Base.classes, TABLE)

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)


def get_data():
    col = getattr(SA_TABLE, COLUMN)
    rows = session.query(col).filter(
        and_(col != None, col != '')  # noqa E711
    )
    cnt = Counter()
    for row in rows:
        attr = row[0]

        if isinstance(attr, datetime):
            attr = attr.strftime("%Y-%m")

        cnt[attr] += 1
    return sorted(cnt.items())


def is_valid_template(template_name):
    template_names = [os.path.splitext(template)[0]
                      for template in os.listdir(TEMPLATE_FOLDER)]
    return template_name in template_names


def calculate_max_height_graph(values):
    max_value = max(values)
    return int(ceil(max_value / 100.0)) * 100


def get_colors(values):
    colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
              "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
              "#C71585", "#FF4500"]
    return islice(cycle(colors), len(values))


@app.route('/')
@app.route('/<template_name>')
def show_data(template_name=None):
    template_name = template_name if template_name else DEFAULT_TEMPLATE
    if not is_valid_template(template_name):
        abort(400, 'Not a valid template')

    data = get_data()
    labels, values = zip(*data)
    max_height = calculate_max_height_graph(values)

    kwargs = {}
    if template_name == "pie":
        colors = get_colors(values)
        kwargs = {
            "set": zip(values, labels, colors)
        }

    return render_template(f'{template_name}.html',
                           title=f"{TABLE} - {COLUMN}",
                           labels=labels,
                           values=values,
                           max_height=max_height,
                           **kwargs)
