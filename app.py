from collections import Counter
from datetime import datetime
from itertools import cycle, islice
from math import ceil
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request, abort

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
SEPARATOR = "++"
TEMPLATE_FOLDER = "templates"
DEFAULT_TEMPLATE = "index"

engine = create_engine(DATABASE_URL)
session = sessionmaker(engine)()

metadata = MetaData()
metadata.reflect(engine)

Base = automap_base(metadata=metadata)
Base.prepare()

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)


def get_data(table, column):
    SA_TABLE = getattr(Base.classes, table)
    col = getattr(SA_TABLE, column)
    rows = session.query(col).all()
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


@app.route('/columns')
def show_columns():
    table_str = request.args.get("table")
    table = Base.classes.get(table_str)
    table_columns = {
        col: f"{table_str}{SEPARATOR}{col}" for col in
        table.__table__.columns.keys()
    }
    return render_template(
        '_columns.html',
        table_columns=sorted(table_columns.items())
    )


@app.route('/graph')
def build_graph():
    tcolumn = request.args["tcolumn"]
    table, column = tcolumn.split(SEPARATOR)
    data = get_data(table, column)
    labels, values = zip(*data)
    max_height = calculate_max_height_graph(values)
    return render_template(
        '_graph.html',
        labels=labels,
        values=values,
        max_height=max_height
    )


@app.route('/')
@app.route('/<template_name>')
def show_data(template_name=None):
    template_name = template_name if template_name else DEFAULT_TEMPLATE
    if not is_valid_template(template_name):
        abort(400, 'Not a valid template')

    table = "auth_user"
    column = "date_joined"
    data = get_data(table, column)
    labels, values = zip(*data)
    max_height = calculate_max_height_graph(values)

    kwargs = {}
    if template_name == "pie":
        colors = get_colors(values)
        kwargs = {
            "set": zip(values, labels, colors)
        }

    tables = sorted(Base.classes.keys())

    return render_template(f'{template_name}.html',
                           #title=f"{TABLE} - {COLUMN}",
                           title="my title",
                           tables=tables,
                           labels=labels,
                           values=values,
                           max_height=max_height,
                           **kwargs)
