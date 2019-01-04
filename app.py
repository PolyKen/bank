from flask import Flask, render_template
from db import *
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/table/<table_name>'])
def get_table(table_name):
    print(blue(table_name))
    heads = User.head()
    all_fields_name = [field[0] for field in heads]
    d = {"thead": all_fields_name, "tbody": User.select()}
    return json.dumps(d)


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
