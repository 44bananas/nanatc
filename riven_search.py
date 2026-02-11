#riven_search
from flask import Flask
from flask import Flask, request
import sqlite3
import json
import translator_search
import base64
from datetime import datetime

app = Flask(__name__)


@app.route("/riven_search_trash")
def riven_trash():
    with open("weapon_info.json") as json_file:
        weapons = json.load(json_file)
    weapon = request.args.get("weapon", default="").title()
    print(weapon)
    if weapon not in weapons:
        return
    if weapon == "":
        return
    dictionary = {}
    con = sqlite3.connect("tc.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    if weapon in weapons:
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ?",(weapon,))
    else:
        return
    try:
        db = db.fetchall()
        for i in range(len(db)):
            dictionary.update({i:{"username":db[i][0],"weapon":db[i][1],"prefix":db[i][2],"stat1":db[i][3],"stat2":db[i][4],"stat3":db[i][5],"neg":db[i][6],"date":datetime.fromtimestamp(float(db[i][7])),"message":db[i][8],"price":db[i][9],"negval":db[i][12],"stat1val":db[i][13],"stat2val":db[i][14],"stat3val":db[i][15]}})
    except:
        return "Failed"
    return dictionary
    
@app.route("/riven_search")
def riven_search():
    #get weapons
    with open("weapon_info.json") as json_file:
        weapons = json.load(json_file)
    weapon = request.args.get("weapon", default="").title()
    pos1 = request.args.get("pos1", default="[]").lower()
    pos2 = request.args.get("pos2", default="[]").lower()
    pos3 = request.args.get("pos3", default="[]").lower()
    neg = request.args.get("neg", default="[]").lower()
    if weapon not in weapons:
        return
    if weapon == "" and pos1 == "[]" and pos2 == "[]" and pos3 == "[]" and neg == "[]":
        return
    if pos1 != "[]":
        pos1 = translator_search.translate_riven_img(translator_search.translate(pos1)).replace("Base Damage / Melee Damage","Damage")
    if pos2 != "[]":
        pos2 = translator_search.translate_riven_img(translator_search.translate(pos2)).replace("Base Damage / Melee Damage","Damage")
    if pos3 != "[]":
        pos3 = translator_search.translate_riven_img(translator_search.translate(pos3)).replace("Base Damage / Melee Damage","Damage")
    if neg != "[]":
        neg = translator_search.translate_riven_img(translator_search.translate(neg)).replace("Base Damage / Melee Damage","Damage")
    try:
        if weapons[weapon]["type"] == 'melee':
            pos1 = pos1.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
            pos2 = pos2.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
            pos3 = pos3.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
            neg = neg.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
        if weapons[weapon]["type"] == 'rifle' or weapons[weapon]["type"] == 'shotgun':
            pos1 = pos1.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
            pos2 = pos2.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
            pos3 = pos3.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
            neg = neg.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
        if weapons[weapon]["type"] == 'pistol' or weapons[weapon]["type"] == 'kitgun' or weapons[weapon]["type"] == 'archgun':
            pos1 = pos1.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
            pos2 = pos2.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
            pos3 = pos3.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
            neg = neg.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
    except:
        weapon = weapon.lower()
        if weapon == "melee":
            pos1 = pos1.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
            pos2 = pos2.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
            pos3 = pos3.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
            neg = neg.replace("Fire Rate / Attack Speed","Attack Speed").replace("Base Damage / Melee Damage","Damage")
        if weapon == "rifle" or weapon == "shotgun":
            pos1 = pos1.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
            pos2 = pos2.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
            pos3 = pos3.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
            neg = neg.replace("Fire Rate / Attack Speed","Fire Rate(x2 for Bows)").replace("Base Damage / Melee Damage","Damage")
        if weapon == "pistol" or weapon == "kitgun" or weapon == "archgun":
            pos1 = pos1.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
            pos2 = pos2.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
            pos3 = pos3.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
            neg = neg.replace("Fire Rate / Attack Speed","Fire Rate").replace("Base Damage / Melee Damage","Damage")
    dictionary = {}
    con = sqlite3.connect("tc.db",isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    print(weapon, pos1, pos2, pos3, neg)
    #specific weapon + specific pos + specific neg
    if (weapon != "melee" and weapon != "shotgun" and weapon != "rifle" and weapon != "pistol" and weapon != "kitgun" and weapon != "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat = ? ",(weapon, pos1,pos1,pos1, pos2,pos2,pos2, pos3,pos3,pos3, neg,))
    #specific weapon + specific pos + any neg
    elif (weapon != "melee" and weapon != "shotgun" and weapon != "rifle" and weapon != "pistol" and weapon != "kitgun" and weapon != "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg == "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat != ? ",(weapon, pos1,pos1,pos1, pos2,pos2,pos2, pos3,pos3,pos3, '[]',))
    #specific weapon + specific dual stat + specific neg
    elif (weapon != "melee" and weapon != "shotgun" and weapon != "rifle" and weapon != "pistol" and weapon != "kitgun" and weapon != "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 == "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat = ? ",(weapon, pos1,pos1,pos1, pos2,pos2,pos2, '[]','[]','[]', neg,))
    #specific weapon + specific dual stat + any neg
    elif (weapon != "melee" and weapon != "shotgun" and weapon != "rifle" and weapon != "pistol" and weapon != "kitgun" and weapon != "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg == "1" and pos1 != "[]" and pos2 != "[]" and pos3 == "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat != ? ",(weapon, pos1,pos1,pos1, pos2,pos2,pos2, '[]','[]','[]', '[]',))
    #any weapon + specific pos + specific neg
    elif (weapon == "melee" or weapon == "shotgun" or weapon == "rifle" or weapon == "pistol" or weapon == "kitgun" or weapon == "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat = ? ",( pos1,pos1,pos1, pos2,pos2,pos2, pos3,pos3,pos3, neg,))
    #any weapon + specific pos + any neg
    elif (weapon == "melee" or weapon == "shotgun" or weapon == "rifle" or weapon == "pistol" or weapon == "kitgun" or weapon == "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat != ? ",( pos1,pos1,pos1, pos2,pos2,pos2, pos3,pos3,pos3, '[]',))
    #any weapon + specific dual stat + specific neg
    elif (weapon == "melee" or weapon == "shotgun" or weapon == "rifle" or weapon == "pistol" or weapon == "kitgun" or weapon == "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat = ? ",( pos1,pos1,pos1, pos2,pos2,pos2, '[]','[]','[]', neg,))
    #any weapon + specific dual stat + any neg
    elif (weapon == "melee" or weapon == "shotgun" or weapon == "rifle" or weapon == "pistol" or weapon == "kitgun" or weapon == "archgun") and pos1 != "1" and pos2 != "1" and pos3 != "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat != ? ",( pos1,pos1,pos1, pos2,pos2,pos2, '[]','[]','[]', '[]',))
    #any weapon + speicfic 2 stats + any 3rd stat + specific neg
    elif (weapon == "melee" or weapon == "shotgun" or weapon == "rifle" or weapon == "pistol" or weapon == "kitgun" or weapon == "archgun")  and pos1 != "1" and pos2 != "1" and pos3 == "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat = ? ",( pos1,pos1,pos1, pos2,pos2,pos2, neg,))
    #any weapon + specific 2 stats + any 3rd stat + any neg
    elif (weapon == "melee" or weapon == "shotgun" or weapon == "rifle" or weapon == "pistol" or weapon == "kitgun" or weapon == "archgun") and pos1 != "1" and pos2 != "1" and pos3 == "1" and neg == "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat != ? ",( pos1,pos1,pos1, pos2,pos2,pos2, "[]",))
    #specific weapon + any stats + specific neg
    elif (weapon != "melee" and weapon != "shotgun" and weapon != "rifle" and weapon != "pistol" and weapon != "kitgun" and weapon != "archgun") and neg != "[]" and neg != "1":
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND negstat = ? ",(weapon, neg,))    
    #specific weapon + specific 2 stats and any 3rd stat + specific neg
    elif (weapon != "melee" and weapon != "shotgun" and weapon != "rifle" and weapon != "pistol" and weapon != "kitgun" and weapon != "archgun") and pos1 != "1" and pos2 != "1" and pos3 == "1" and neg != "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat = ? ",(weapon, pos1,pos1,pos1, pos2,pos2,pos2, neg,))
    #specific weapon + specific 2 stats and any 3rd stat + any neg
    elif (weapon != "melee" and weapon != "shotgun" and weapon != "rifle" and weapon != "pistol" and weapon != "kitgun" and weapon != "archgun") and pos1 != "1" and pos2 != "1" and pos3 == "1" and neg == "1" and pos1 != "[]" and pos2 != "[]" and pos3 != "[]" and neg != "[]":
        db = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND (stat1stat = ? OR stat2stat = ? OR stat3stat = ?) AND negstat != ? ",(weapon, pos1,pos1,pos1, pos2,pos2,pos2, "[]",))

    try:
        db = db.fetchall()
        for i in range(len(db)):
            dictionary.update({i:{"username":db[i][0],"weapon":db[i][1],"prefix":db[i][2],"stat1":db[i][3],"stat2":db[i][4],"stat3":db[i][5],"neg":db[i][6],"date":datetime.fromtimestamp(float(db[i][7])),"message":db[i][8],"price":db[i][9],"image":str(base64.b64decode(db[i][10])),"negval":db[i][12],"stat1val":db[i][13],"stat2val":db[i][14],"stat3val":db[i][15]}})
    except:
        return "Failed"
    return dictionary

while True:
    app.run(host='10.0.0.61',port=4242)
