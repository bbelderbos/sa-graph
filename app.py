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


def _roundup(number):
    return int(math.ceil(number / 100.0)) * 100


def _calc_max(values):
    return _roundup(max(values))


@app.route('/')
def show_data():
    data = get_data()
    labels, values = zip(*data)
    return render_template('index.html', title='New users on the platform',
                           labels=labels, values=values, max=_calc_max(values))
