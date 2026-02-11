#flask_test

from flask import Flask
from flask import Flask, request
import sqlite3
from datetime import datetime
import base64
import time
# import datetime

app = Flask(__name__)

@app.route("/tc")
def wfm_rivens():
    time_to_check = time.time() - 600
    dictionary = {}
    con = sqlite3.connect("tc.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    db = cur.execute("SELECT * FROM rivens WHERE date > ?",(time_to_check,))
    db = db.fetchall()
    for i in range(len(db)):
        dictionary.update({i:{"user":db[i][0],"weapon":db[i][1],"prefix":db[i][2],"price":db[i][9],"date":datetime.fromtimestamp(float(db[i][7])),"message":db[i][8],"first_stat":db[i][3],"second_stat":db[i][4],"third_stat":db[i][5],"neg_stat":db[i][6],"image":str(base64.b64decode(db[i][10])),"neg_val":db[i][12],"first_stat_val":db[i][13],"second_stat_val":db[i][14],"third_stat_val":db[i][15],"raw_stat1":db[i][16],"raw_stat2":db[i][17],"raw_stat3":db[i][18],"raw_negstat":db[i][19]}})
    return dictionary
@app.route("/tc_noimg")
def wfm_rivens_noimg():
    time_to_check = time.time() - 600
    dictionary = {}
    con = sqlite3.connect("tc.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    db = cur.execute("SELECT * FROM rivens WHERE date > ?",(time_to_check,))
    db = db.fetchall()
    for i in range(len(db)):
        dictionary.update({i:{"user":db[i][0],"weapon":db[i][1],"prefix":db[i][2],"price":db[i][9],"date":datetime.fromtimestamp(float(db[i][7])),"message":db[i][8],"first_stat":db[i][3],"second_stat":db[i][4],"third_stat":db[i][5],"neg_stat":db[i][6],"neg_val":db[i][12],"first_stat_val":db[i][13],"second_stat_val":db[i][14],"third_stat_val":db[i][15],"raw_stat1":db[i][16],"raw_stat2":db[i][17],"raw_stat3":db[i][18],"raw_negstat":db[i][19]}})
    return dictionary

@app.route("/48hrs")
def twodays():
    time_to_check = time.time() - 172800
    dictionary = {}
    con = sqlite3.connect("tc.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    db = cur.execute("SELECT * FROM rivens WHERE date > ?",(time_to_check,))
    db = db.fetchall()
    for i in range(len(db)):
        dictionary.update({i:{"user":db[i][0],"weapon":db[i][1],"prefix":db[i][2],"price":db[i][9],"date":datetime.fromtimestamp(float(db[i][7])),"message":db[i][8],"first_stat":db[i][3],"second_stat":db[i][4],"third_stat":db[i][5],"neg_stat":db[i][6],"neg_val":db[i][12],"first_stat_val":db[i][13],"second_stat_val":db[i][14],"third_stat_val":db[i][15],"raw_stat1":db[i][16],"raw_stat2":db[i][17],"raw_stat3":db[i][18],"raw_negstat":db[i][19]}})
    return dictionary

# @app.route("/tc_items")
# def tc_items():
#     dictionary = {}
#     con = sqlite3.connect("arcane_prime_parts.db",isolation_level=None)
#     con.execute('pragma journal_mode=wal;')
#     cur = con.cursor()
#     db = cur.execute("SELECT * FROM data WHERE date = ?",(str(datetime.date.today()),))
#     db = db.fetchall()
#     for i in range(len(db)):
#         dictionary.update({i:{"wtb-wts":db[i][0],"user":db[i][1],"price":db[i][2],"identifier":db[i][3],"date":db[i][4],"item":db[i][5],"message":db[i][6],"rank":db[i][7]}})
#     return dictionary

# @app.route("/tc_items_search")
# def tc_items_search():
#     itemname = request.args.get("item", default="").lower()
#     wtb_wts = request.args.get("wtbwts", default="").lower()
#     print(itemname)
#     if itemname == "":
#         return
#     dictionary = {}
#     con = sqlite3.connect("arcane_prime_parts.db",isolation_level=None)
#     con.execute('pragma journal_mode=wal;')
#     cur = con.cursor()
#     if wtb_wts == "":
#         db = cur.execute("SELECT * FROM data WHERE item = ?",(itemname,))
#     if wtb_wts == "wtb" or wtb_wts == "wts":
#         db = cur.execute("SELECT * FROM data WHERE item = ? AND wtbwts = ?",(itemname,wtb_wts,))
#     db = db.fetchall()
#     for i in range(len(db)):
#         dictionary.update({i:{"wtbwts":db[i][0],"user":db[i][1],"price":db[i][2],"date":db[i][4],"item":db[i][5],"message":db[i][6],"rank":db[i][7]}})
#     return dictionary

while True:
    app.run(host='10.0.0.61')
