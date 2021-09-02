from collections import Counter
from datetime import date
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
USER_TABLE_NAME = os.environ["USER_TABLE_NAME"]
PROFILE_TABLE_NAME = os.environ["PROFILE_TABLE_NAME"]
GEO_COLUMN = os.environ["GEO_COLUMN"]
JOINED_COLUMN = os.environ["JOINED_COLUMN"]

engine = create_engine(DATABASE_URL)
session = sessionmaker(engine)()

metadata = MetaData()
metadata.reflect(engine, only=[USER_TABLE_NAME, PROFILE_TABLE_NAME])

Base = automap_base(metadata=metadata)
Base.prepare()

USER_TABLE = getattr(Base.classes, USER_TABLE_NAME)
PROFILE_TABLE = getattr(Base.classes, PROFILE_TABLE_NAME)

LAST_YEAR = date.today().year - 1
START_DATE = date(LAST_YEAR, 1, 1)
COLORS = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


def _get_data_acquisition(start_date=START_DATE):
    col = getattr(USER_TABLE, JOINED_COLUMN)
    users = session.query(col).all()
    cnt = Counter()
    for user in users:
        date_joined = user[0]
        if date_joined.date() < start_date:
            continue
        cnt[date_joined.strftime("%Y-%m")] += 1
    return sorted(cnt.items())


def _get_data_user_geos():
    col = getattr(PROFILE_TABLE, GEO_COLUMN)
    profiles = session.query(col).filter(
        and_(col != None, col != '')  # noqa E711
    )
    cnt = Counter(x[0].split("/")[0] for x in profiles.all())
    return cnt.items()


def _roundup(number):
    return int(math.ceil(number / 100.0)) * 100


def _calc_max(values):
    return _roundup(max(values))


@app.route('/')
def show_user_acquisition():
    data = _get_data_acquisition()
    labels, values = zip(*data)
    return render_template('index.html', title='New users on the platform',
                           labels=labels, values=values, max=_calc_max(values))


@app.route('/geos')
def show_user_geos():
    data = _get_data_user_geos()

    data = dict((k, v) for k, v in data if v > 10)

    data["US"] += data["America"]
    del data["America"]

    labels, values = zip(*data.items())

    return render_template('geos.html', title='Top geos platform users',
                           set=zip(values, labels, COLORS))
