#/!usr/bin/env python3

from flask import Flask, render_template
from flask_bootstrap import Bootstrap

import pymongo

app = Flask(__name__)
bootstrap = Bootstrap(app)

connection = pymongo.MongoClient("mongodb://localhost")

db = connection.pharmacy
medicine = db.medicine


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)