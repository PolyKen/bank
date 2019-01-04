from flask import Flask, render_template
from db import *
import datetime
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/table/<table_name>')
def get_table(table_name):
    print(blue(table_name))
    rows_list = list(map(lambda o: dict(o), User.select()))
    for i in range(len(rows_list)):
        row = rows_list[i]
        if "start_time" in row:
            row["start_time"] = row["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        if "birthday" in row:
            row["birthday"] = row["birthday"].strftime("%Y-%m-%d")
    return json.dumps(rows_list)


@app.route('/test')
def test():
    try:
        print("donothing")
    except Exception as e:
        print(e)
        return str(e)
    return 'test success'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
