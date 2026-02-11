#dbitems_to_api
from flask import Flask
from flask import Flask, request
import sqlite3
import datetime 
import json

app = Flask(__name__)

@app.route("/tc_items")
def tc_items():
    dictionary = {}
    con = sqlite3.connect("arcane_prime_parts.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    db = cur.execute("SELECT * FROM data WHERE date = ?",(str(datetime.date.today()),))
    db = db.fetchall()
    for i in range(len(db)):
        dictionary.update({i:{"wtb-wts":db[i][0],"user":db[i][1],"price":db[i][2],"identifier":db[i][3],"date":db[i][4],"item":db[i][5],"message":db[i][6],"rank":db[i][7]}})
    return dictionary

@app.route("/tc_items_search")
def tc_items_search():
    with open("parts.txt") as json_file:
        item_infos = json.load(json_file)
    itemname = request.args.get("item", default="").lower()
    wtb_wts = request.args.get("wtbwts", default="").lower()
    print(itemname)
    if itemname == "":
        return
    dictionary = {}
    if itemname not in item_infos:
        return
    con = sqlite3.connect("arcane_prime_parts.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    if wtb_wts == "":
        db = cur.execute("SELECT * FROM data WHERE item = ?",(itemname,))
    if wtb_wts == "wtb" or wtb_wts == "wts":
        db = cur.execute("SELECT * FROM data WHERE item = ? AND wtbwts = ?",(itemname,wtb_wts,))
    db = db.fetchall()
    for i in range(len(db)):
        dictionary.update({i:{"wtbwts":db[i][0],"user":db[i][1],"price":db[i][2],"date":db[i][4],"item":db[i][5],"message":db[i][6],"rank":db[i][7]}})
    return dictionary

while True:
    app.run(host='10.0.0.61',port=6969)
