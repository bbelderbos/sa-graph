from collections import Counter
from datetime import datetime
import math
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template

load_dotenv()
app = Flask(__name__)

DATABASE_URL = os.environ["DATABASE_URL"]
TABLE = os.environ["TABLE"]
COLUMN = os.environ["COLUMN"]

engine = create_engine(DATABASE_URL)
session = sessionmaker(engine)()

metadata = MetaData()
metadata.reflect(engine, only=[TABLE])

Base = automap_base(metadata=metadata)
Base.prepare()

SA_TABLE = getattr(Base.classes, TABLE)


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


def calculate_max_height_graph(values):
    max_value = max(values)
    return int(math.ceil(max_value / 100.0)) * 100


@app.route('/')
def show_data():
    data = get_data()
    labels, values = zip(*data)
    return render_template('index.html', title=f"{TABLE} - {COLUMN}",
                           labels=labels, values=values,
                           max_height=calculate_max_height_graph(values))
