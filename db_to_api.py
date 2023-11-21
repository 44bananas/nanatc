#flask_test

from flask import Flask
import sqlite3
from datetime import datetime
import base64

app = Flask(__name__)


@app.route("/tc")
def wfm_rivens():
    dictionary = {}
    con = sqlite3.connect("tc.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    db = cur.execute("SELECT * FROM (SELECT * FROM rivens ORDER BY date DESC LIMIT 50) ORDER BY date DESC")
    db = db.fetchall()
    for i in range(len(db)):
        dictionary.update({i:{"user":db[i][0],"weapon":db[i][1],"prefix":db[i][2],"price":db[i][9],"date":datetime.fromtimestamp(float(db[i][7])),"message":db[i][8],"first_stat":db[i][3],"second_stat":db[i][4],"third_stat":db[i][5],"neg_stat":db[i][6],"image":str(base64.b64decode(db[i][10]))}})
    return dictionary

while True:
    app.run(host='ip goes here')
