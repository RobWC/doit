#!/usr/bin/python

from flask import Flask
from flask import render_template

app = Flask(__name__, static_url_path='')
app.debug = True

@app.route('/')
def index():
  return render_template('dashboard.j2', title="Dashboard")

@app.route('/domains')
def domains():
  return render_template('domains.j2',title="Domains")

if __name__ == '__main__':
  app.run(host="0.0.0.0",port=int("12345"))
