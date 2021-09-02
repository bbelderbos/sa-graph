# DB graphs

Uses SA automap to load in a table and makes a graph of a the counts of a specific column.

Big shout-out to Ruan Bekker's [Graphing Pretty Charts With Python Flask and Chartjs](https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/) which made the graphing part very easy.

## Setup

```
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env-template .env
# set env variables
flask run
```
