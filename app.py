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
    def construct_dict(fields, values):
        d = {}
        for i, field in enumerate(fields):
            d[field] = values[i]
        return d

    heads = get_head(table_name)
    if heads is None:
        return "table not found"
    all_fields_name = [field[0] for field in heads]
    select_sql = 'SELECT ? FROM {}'.format(table_name)
    results = execute_sql(select_sql, "*")
    rows_list = list(map(lambda v: construct_dict(all_fields_name, v), results))

    for i in range(len(rows_list)):
        row = rows_list[i]
        if "start_time" in row:
            row["start_time"] = row["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        if "birthday" in row:
            row["birthday"] = row["birthday"].strftime("%Y-%m-%d")
        if "level_update_time" in row:
            row["level_update_time"] = row["level_update_time"].strftime("%Y-%m-%d %H:%M:%S")

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
