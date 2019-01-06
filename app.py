from flask import Flask, render_template, request
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
        if "update_time" in row:
            row["update_time"] = row["update_time"].strftime("%Y-%m-%d %H:%M:%S")
        if "level_update_time" in row:
            row["level_update_time"] = row["level_update_time"].strftime("%Y-%m-%d %H:%M:%S")

    return json.dumps({"heads_list": all_fields_name, "rows_list": rows_list})


@app.route('/deposit')
def deposit():
    user_id = request.args.get('user_id')
    account_id = request.args.get('account_id')
    quantity = request.args.get('quantity')
    currency_type = request.args.get('currency_type')
    deposit_type = request.args.get('deposit_type')

    a = Account.query(id=account_id, user_id=user_id)

    if a is None:
        NotMatch.print()
        return "not match error"

    if quantity is None or currency_type is None or deposit_type is None:
        InvalidParameter.print()
        return "invalid parameter error"

    a.deposit(quantity=quantity, currency_type=currency_type, deposit_type=deposit_type)
    return "success"


@app.route('/withdraw')
def withdraw():
    user_id = request.args.get('user_id')
    account_id = request.args.get('account_id')
    quantity = request.args.get('quantity')

    a = Account.query(id=account_id, user_id=user_id)

    if a is None:
        NotMatch.print()
        return "not match error"

    if quantity is None:
        InvalidParameter.print()
        return "invalid parameter error"

    return a.withdraw(quantity=quantity)


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
