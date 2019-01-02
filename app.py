from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
