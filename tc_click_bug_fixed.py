import grequests
import time
from ahk import AHK
import PIL.ImageGrab as ImageGrab
import logging
import json
import Levenshtein
import pyautogui
import re
import pytesseract
from pytesseract import Output
import sqlite3
import base64
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import datetime
import win32gui, win32con

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='tc_click.log', filemode='a')
ahk = AHK(executable_path=r'AutoHotkey\\AutoHotkey.exe')
# ahk = AHK()
pytesseract.pytesseract.tesseract_cmd = (r"Tesseract-OCR\\tesseract.exe")

time.sleep(5)
warframewindow = win32gui.FindWindow(None, "Warframe")

#varrs needed
prefix_suffix_list = ['Laci','Nus','Ampi','Bin','Argi','Con','Pura','Ada','Manti','Tron','Geli','Do','Toxi','Tox','Igni','Pha','Vexi','Tio','Crita','Cron','Pleci','Nent','Acri','Tis','Visi','Ata','Exi','Cta','Croni','Dra','Conci','Nak','Para','Um','Magna','Ton','Insi','Cak','Sci','Sus','Arma','Tin','Forti','Us','Sati','Can','Lexi','Nok','Feva','Tak','Locti','Tor','Hexa','Dex','Deci','Des','Zeti','Mag','Hera','Lis','Tempi','Nem']
stat_names = ["Additional Combo Count Chance","Chance to Gain Combo Count","Fire Rate","Fire Rate(x2 for Bows)","Attack Speed","Ammo Maximum","Damage to Corpus","Damage to Grineer","Damage to Infested","Cold","Combo Duration","Critical Chance","Critical Chance (x2 for Heavy Attacks)","Critical Chance for Slide attack","Critical Damage","Damage","Melee damage","Electricity","Heat","Punch Through","Finisher Damage","Projectile Speed","Initial Combo","Impact","Magazine Capacity","Heavy Attack Efficiency","Multishot","Status Chance","Toxin","Puncture","Reload Speed","Range","Slash","Status Duration","Weapon Recoil","Zoom"]

#get weapons
with open("weapon_info.json") as json_file:
    weapons = json.load(json_file)

with open('data.txt', 'r') as data:
    data = json.load(data)
with open('parts.txt', 'r') as parts:
    parts = json.load(parts)
list_of_items = []
for item in data:
    list_of_items.append(item.replace("_", " ").lower().replace(" set","").replace("set",""))

weapon_names = []
for each in weapons:
    for i in weapons[each]['variants']:
        weapon_names.append(i.replace(" Primary","").replace(" Secondary",""))

def check_message(chat_message):
    chat_message = chat_message.lower()
    try:
        username = is_account(re.sub(r"[\[\]]","",str(re.findall(r"(?<=\[[0-9]{2}\:[0-9]{2}\])(.*?)(?=:)",str(chat_message))[0])).strip())[1]
    except:
        return
    timestamp = re.findall(r"\[[0-9]{2}.*[0-9]{2}\]{1}",chat_message)[0]
    if any([i for i in list_of_items if i in chat_message]):
        items_in_message = re.findall(r"(?<=\[)(.*?)(?=\])",chat_message.replace(timestamp,""))
        prices = [re.sub(r"[\[{].*?[\]|}]", " ",i.replace("o","0")).strip() for i in re.findall(r"[\[{].*?[\]|}] *[0-9o]*[.,]?[0-9o]*k?p?w?",str(chat_message.replace(timestamp,"")).lower())]
        for item, price in zip(items_in_message, prices):
            if price == "0":
                price = ""
            try:
                if chat_message[chat_message.find(item)+len(item)+2] == "r" or chat_message[chat_message.find(item)+len(item)+1] == "r":
                    try:
                        rank = re.findall(r"(?<=[r])[0-9]",chat_message[chat_message.find(item):])[0]
                    except:
                        rank = 0
                else:
                    rank = "0"
            except:
                continue
            if chat_message.replace(timestamp,"").find(price) < chat_message.find(item):
                try:
                    price = re.findall(r"[.*?[\]|}] *\d*[.,]?\d*k?p?w?",str(chat_message.replace(timestamp,"").replace("r"+rank,"")[chat_message.find(item):]).lower())[0].replace("]","").strip()
                except:
                    continue
            try:
                price = re.findall(r"\d+",price)[0].strip()
            except:
                continue
            if chat_message.replace(timestamp,"").find(price) < chat_message.find(item):                
                continue
            wts_index = chat_message[:chat_message.find(item)].find("wts")
            wtb_index = chat_message[:chat_message.find(item)].find("wtb")
            item_index = chat_message.find(item)
            if wts_index - item_index > wtb_index - item_index and price != "0" and price != "1":
                con = sqlite3.connect("arcane_prime_parts.db")
                con.execute("INSERT OR IGNORE INTO data ('wtbwts', username, price, identifier, date, item, message, rank) values(?, ?, ?, ?, ?, ?, ?, ?)",
                    ("wts",username,price,"wts" + username + price + str(datetime.date.today()),str(datetime.date.today()), url_name(item), chat_message, rank))
                con.commit()
            if wts_index - item_index < wtb_index - item_index and price != "0" and price != "1":
                con = sqlite3.connect("arcane_prime_parts.db")
                con.execute("INSERT OR IGNORE INTO data ('wtbwts', username, price, identifier, date, item, message, rank) values(?, ?, ?, ?, ?, ?, ?, ?)",
                    ("wtb",username,price,"wtb" + username + price + str(datetime.date.today()),str(datetime.date.today()), url_name(item), chat_message, rank))
                con.commit()

def find_match(stat):
    for stats in stat_names:
        if "infested" in stat.lower() and Levenshtein.jaro_winkler(stat.lower(), stats.lower()) > 0.921: 
            return stats
        elif Levenshtein.jaro_winkler(stat.lower(), stats.lower()) > 0.894 and "infested" not in stat.lower():            
            if "heavy" in stats.lower() and "slide" in stat.lower():
                continue
            return stats
        else:
            continue
    if stat.lower() == "almpact":
        return "Impact"
    if stat.lower() == "3kcold":
        return "Cold"
    if stat.lower() == "3 cold":
        return "Cold"
    if stat.lower() == "4 heat":
        return "Heat"
    return stat
ready_to_check = False

def url_name(grabbed):
    for each in parts:
        if grabbed.lower() == each['item_name'].lower().replace("_set","").replace(" set",""):
            return each['url_name']
    return grabbed

def is_account(ign):
    ign = ign.strip()
    if [i.text for i in grequests.map(grequests.get(u) for u in ["http://10.0.0.38:5000/username_query?username=" + ign.lower()])][0] == "True":
        logging.info("account in db")
        return True, ign
    # xbox = "https://content-xb1"
    # psn = "https://content-ps4"
    # pc = "https://content"
    # mobile = "https://content-mob"
    # url = ".warframe.com/1/dynamic/getProfileViewingData.php?n="
    # logging.info("before requests")
    # data = grequests.map(grequests.get(u) for u in [pc + url + ign, psn + url + ign, xbox + url + ign, mobile + url + ign])
    # logging.info("after requests")
    # is_account_real = False
    # for i in data:
    #     try:
    #         if "Retry PC account:" in i.text:
    #             is_account_real = True
    #         elif i.status_code == 400 or i.status_code == 409:
    #             continue
    #         else:
    #             is_account_real = True
    #     except:
    #         is_account_real = False
    #         logging.info("account check failed")
    is_account_real = True
    return is_account_real, ign

def ocr_error(stats):
    stats = stats.strip()
    if "--" in stats:
        stats = stats[1:]
    try:
        
        if stats[0] =="X":
            stats = stats[1:]
        if stats[0] =="x":
            stats = stats[1:]
        if stats[0] ==".":
            stats = stats[1:]
        if stats[0] =="%":
            stats = stats[1:]
    except:
        logging.info("no neg")
    return stats

def closed_chat():  
    img2 = ImageGrab.grab(bbox=(250, 670, 500, 750))
    #turn image to data
    img_loc2 = pytesseract.image_to_data(img2, output_type=Output.DICT, config="--psm 6 -c preserve_interword_spaces=1 -c tessedit_char_whitelist=\r' []01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-.:'")
    if "options" in str(img_loc2['text']).lower():
        logging.info("T")
        pyautogui.moveTo(950,550)
        ahk.click()
        ahk.send("T")
        
def tc_scraper():
    # pyautogui.getWindowWithTitle("Warframe")[0].activate()
    win32gui.SetForegroundWindow(warframewindow)
    win32gui.ShowWindow(warframewindow,win32con.SW_MAXIMIZE)
    ahk.click()
    hit_escape = False
    closed_chat()
    pyautogui.moveTo(950,550)
    ahk.send("{WheelDown 50}")
    todays_date = time.time()
    #take a ss of tc
    #(left_x, top_y, right_x, bottom_y)
    left_x = 0
    # top_y = 950
    top_y = 860
    # top_y = 650
    # top_y = 770
    right_x = 1007
    bottom_y = 985
    #scroll up
    time.sleep(0.2)
    pyautogui.moveTo(950,550)
    ahk.send("{WheelUp 10}")
    time.sleep(0.2)
    #put boxes on pc and console icons
    img1 = ImageGrab.grab(bbox=(left_x, top_y, right_x, bottom_y))
    wf = np.array(img1)[:,:,::-1].copy()
    wf_grayscale = cv2.cvtColor(wf, cv2.COLOR_BGR2GRAY)
    console = cv2.imread("console.png", 0)
    pc = cv2.imread("pc.png", 0)
    for x in [pc, console]:
        w, h = x.shape[::-1]
        res = cv2.matchTemplate(wf_grayscale, x, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(wf, pt, (pt[0] + w, pt[1] + h), (0, 0, 0), -1)
    img1 = Image.fromarray(wf).convert("L")
    # img1.show()
    #left, bottom, right, top
    #turn image to data
    # img_loc = pytesseract.image_to_data(img1, output_type=Output.DICT, config=r"--psm 6 -c preserve_interword_spaces=1 -c tessedit_char_whitelist=' []01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-.:'")
    img_loc = pytesseract.image_to_data(img1, output_type=Output.DICT, config="--psm 6 -c preserve_interword_spaces=1 -c tessedit_char_blacklist=<>€®™§!@#$%^&*()")
    logging.info("turn tc ss into text")
    #create a tc message out of the data
    # tc_message = " ".join(img_loc['text']).replace("&","").replace("#","").replace("@","").replace("%","")
    tc_message = " ".join(img_loc['text']).replace("€","").replace("®","").replace("™","").replace("§","")
    print(tc_message)
    # print(img_loc)
    #split them into each message
    text_split = [message for message in re.findall(r"[\s\S]*?(?=\[[0-9]{2}.*[0-9]{2}\])",tc_message) if message.strip().lower()]
    for x in text_split:
        check_message(x)
    left_pos = ""
    top_pos = ""
    logging.info("split the text")
    #loop through the data
    for x in range(len(img_loc['level'])):
        #weapon name
        weapon_name_loop_count = 2
        weapon_name = re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-1].lower())
        try:
            while str(weapon_name)[0] != "[" and weapon_name != "":
                if "[" in re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-weapon_name_loop_count].lower()):
                    weapon_name =  re.sub(r'.*\[', "", re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-weapon_name_loop_count].lower())) + " " + weapon_name
                    weapon_name = "[" + weapon_name
                else:
                    weapon_name =  re.sub(r'.*\[', "", re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-weapon_name_loop_count].lower())) + " " + weapon_name
                weapon_name_loop_count += 1
        except:
            continue
        if (weapon_name[0] != "[" and weapon_name[-1] != "]") or weapon_name == '[]' or weapon_name[-1] != "]":
            continue
        link = weapon_name
        weapon_name = weapon_name.replace(re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-1].lower()),"").replace("[","").lower().strip().replace("&", "and")
        prefix_suffix = re.sub(r"\].*","",re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-1].lower())).strip()
        chat_message = [message.strip() for message in text_split if weapon_name in message.lower() and prefix_suffix in message.lower()]
        if any(weapon.lower() in weapon_name for weapon in weapon_names):
            weapon_name = [weapon for weapon in weapon_names if weapon.lower() in weapon_name][0]
        else:
            continue
        username = ""
        try:
            username = re.sub(r"[\[\]]","",str(re.findall(r"(?<=\[[0-9]{2}\:[0-9]{2}\])(.*?)(?=:)",str(chat_message[0]))[0])).strip()
        except:
            username = ""
        if username == "":
            continue
        if username[-2:] == " _":
            username = username[:-2]
        try:
            if len(chat_message[0].lower().replace(username.lower(),"")) > 128:
                continue
        except:
            continue
        #to get price
        try:
            prices = [re.sub(r"[\[{].*?[\]|}]", " ",i.replace("o","0")) for i in re.findall(r"[\[{].*?[\]|}] *[0-9o]*[.,]?[0-9o]*k?p?w?",str(chat_message).lower())]
            links = re.findall(r"[\[{].*?[\]|}]",str(chat_message).lower())
            price = prices[links.index(link.lower())].strip()
            if price == "0":
                price = ""
        except:
            price = ""
        logging.info("parse out the data")
        # if the chat message isnt empty
        if chat_message != []:
            #check if riven name is in it
            if any(suffix.lower() in prefix_suffix.lower() for suffix in prefix_suffix_list) and prefix_suffix.lower() != "mag":
                logging.info("if suffix/prefix")
                #move cursor to where riven name is
                if left_pos == "" and top_pos == "":
                    left_pos = img_loc['left'][x-1] + left_x
                    top_pos = top_y + img_loc['top'][x-1]
                    bottom_pos = top_pos + img_loc['height'][x-1]
                    right_pos = left_pos + img_loc['width'][x-1]
                    xcenter = (left_pos + right_pos) /2
                    ycenter = (top_pos + bottom_pos) /2
                pyautogui.moveTo(xcenter, ycenter)
                time.sleep(0.5)
                ready_to_check = True
                ahk.click()
                ahk.click()
                logging.info("ready to check")
                if ready_to_check == True:
                    loop_count = 5
                    while loop_count > 0:                     
                        #(192, 188, 232)
                        print(ImageGrab.grab(bbox=(820, 350, 1100, 708)).getpixel((28,27)))
                        # ImageGrab.grab(bbox=(820, 350, 1100, 708)).save("color.png")
                        if ImageGrab.grab(bbox=(820, 350, 1100, 708)).getpixel((28,27)) in [(62, 44, 79),(61,43,79),(59,42,78),(60,42,78),(60,42,79),(63,45,79)]:                            
                            #move cursor out of the way
                            pyautogui.moveTo(1000, 1)
                            #take ss
                            image_riven = ImageGrab.grab(bbox=(820, 350, 1100, 708))
                            ahk.click()
                            ahk.send_input("{Esc}")
                            # closed_chat()
                            ready_to_check = False
                            hit_escape = True
                            print("color matched")
                            break
                        time.sleep(0.5)
                        loop_count -= 1
                    if loop_count == 0:
                        # print(ImageGrab.grab(bbox=(820, 350, 1100, 780)).getpixel((28,27)))
                        pyautogui.moveTo(1000, 1)
                        ahk.click()
                        ahk.send_input("{Esc}")
                        time.sleep(0.2)
                        closed_chat()
                        ready_to_check = False
                        left_pos = ""
                        top_pos = ""
                        hit_escape = True
                        continue
                print("before riven ocr")         
                # closed_chat()
                left_pos = ""
                top_pos = ""
                try:
                    image_text = [i for i in re.sub(r"[^A-Za-z0-9\+\-%()\n .]","",pytesseract.image_to_string(image_riven.crop((35, 100, 245, 310)))).strip().splitlines() if i != ""]
                except:
                    # print("failed image text")
                    pyautogui.moveTo(950,550)
                    ahk.send("{WheelDown 50}")
                    ready_to_check = False
                    continue
                logging.info("read riven")
                # print("after riven ocr")
                # assign stats to varriables
                rawnegstat, rawstat1, rawstat2, rawstat3, stat1stat, stat1val, stat2stat, stat2val, stat3stat, stat3val, negstat, negval = "", "", "", "", "", "", "", "", "", "", "", ""
                try:
                    #negstat
                    if "recoil" in image_text[-1].lower():
                        if "-" in image_text[-1]:
                            rawnegstat = ""
                        if "+" in image_text[-1]:
                            rawnegstat = image_text[-1]
                            image_text.remove(image_text[-1])
                    elif "slide attack" in image_text[-1].lower():
                        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                        image_text.remove(image_text[-1])
                        image_text.remove(image_text[-1])
                    elif bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1].lower() and ("-" in image_text[-1] or (bool(re.search(r'[x]\d+\.\d+', image_text[-1].lower())) and  bool(bane in image_text[-1].lower() for bane in ["corpus","grineer","infested"]))):
                        rawnegstat = image_text[-1]
                        image_text.remove(image_text[-1])
                    elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
                        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                        image_text.remove(image_text[-1])
                        image_text.remove(image_text[-1])
                    elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True and ( "-" in image_text[-1] or (bool(re.search(r'[x]\d+\.\d+', image_text[-1].lower())) and  bool(bane in image_text[-1].lower() for bane in ["corpus","grineer","infested"]))):
                        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                        image_text.remove(image_text[-1])
                        image_text.remove(image_text[-1])
                    elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                        image_text.remove(image_text[-1])
                        image_text.remove(image_text[-1])
                    else:
                        rawnegstat = ""

                    #stat1
                    try:
                        if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
                            rawstat1 = image_text[-1]
                            image_text.remove(image_text[-1])
                        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat1 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat1 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat1 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        if "-" in rawstat1 and "recoil" not in rawstat1.lower():
                            rawstat1 = ""
                    except:
                        rawstat1 = ""
                        logging.info("stat 1 break")
                    #stat2
                    try:
                        if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
                            rawstat2 = image_text[-1]
                            image_text.remove(image_text[-1])
                        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat2 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat2 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat2 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        if "-" in rawstat2 and "recoil" not in rawstat2.lower():
                            rawstat2 = ""
                    except:
                        rawstat2 = ""
                        logging.info("stat 2 break")
                    try:
                        if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
                            rawstat3 = image_text[-1].replace("[","").replace("]","")
                            image_text.remove(image_text[-1])
                        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat3 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat3 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                            rawstat3 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                            image_text.remove(image_text[-1])
                            image_text.remove(image_text[-1])
                        if "-" in rawstat3 and "recoil" not in rawstat3.lower():
                            rawstat3 = ""
                    except:
                        rawstat3 = ""
                        logging.info("no stat 3 or stat 3 break")
                    # print("rawr stat parsing done")
                    #extra parsing for ocr errors
                    try:
                        stat1 = ocr_error(rawstat1).strip()
                    except:
                        stat1 = rawstat1.strip()
                        logging.info("stat1 ocr fix error")
                    try:
                        stat2 = ocr_error(rawstat2).strip()
                    except:
                        stat2 = rawstat2.strip()
                        logging.info("stat2 ocr fix error")
                    try:
                        stat3 = ocr_error(rawstat3).strip()
                    except:
                        stat3 = rawstat3.strip()
                        logging.info("stat3 ocr fix error")
                    try:
                        negstat = ocr_error(rawnegstat).strip()
                    except:
                        negstat = rawnegstat.strip()
                        logging.info("negstat ocr fix error")

                    #seperate stat names and values
                    try:
                        stat1val = re.findall(r"\-*\d+\.*\d*",stat1.split(" ")[0])[0]
                        stat1stat = " ".join(stat1.split(" ")[1:])
                    except:
                        stat1val = "0"
                        stat1stat = "[]"
                        logging.info("stat1 failed")
                    try:
                        stat2val = re.findall(r"\-*\d+\.*\d*",stat2.split(" ")[0])[0]
                        stat2stat = " ".join(stat2.split(" ")[1:])
                    except:
                        stat2val = "0"
                        stat2stat = "[]"
                        logging.info("stat2 failed")
                    try:
                        stat3val = re.findall(r"\-*\d+\.*\d*",stat3.split(" ")[0])[0]
                        stat3stat = " ".join(stat3.split(" ")[1:])
                    except:
                        stat3val = "0"
                        stat3stat = "[]"
                        logging.info("stat3 failed")
                    try:
                        negval = re.findall(r"\-*\d+\.*\d*",negstat.split(" ")[0])[0]
                        negstat = " ".join(negstat.split(" ")[1:])
                    except:
                        negval = "0"
                        negstat = "[]"
                        logging.info("negstat failed")      
                    # print("stat parsing done")
                    logging.info("parse info from riven image")
                    #identifier to reduce duplication
                    stat1stat = find_match(stat1stat)
                    stat2stat = find_match(stat2stat)
                    stat3stat = find_match(stat3stat)
                    negstat = find_match(negstat)
                    if stat1stat == "Melee Damage":
                        stat1stat == "Damage"
                    if stat2stat == "Melee Damage":
                        stat2stat == "Damage"
                    if stat3stat == "Melee Damage":
                        stat3stat == "Damage"
                    if negstat == "Melee Damage":
                        negstat == "Damage"
                    prefix_suffixs = []
                    with open("prefix_suffix.json") as json_file:
                        prefix_suffix_json = json.load(json_file)
                    for i in [stat1stat, stat2stat, stat3stat]:
                        try:
                            prefix_suffixs.append(str(prefix_suffix_json[str(i).title()]['prefix']).lower())
                            prefix_suffixs.append(str(prefix_suffix_json[str(i).title()]['suffix']).lower())
                        except:
                            prefix_suffixs.append("")
                            prefix_suffixs.append("")
                    image_text = "".join(image_text)
                    for x in prefix_suffixs:
                        if "vectis" not in image_text.lower():
                            image_text = image_text.lower().replace(x, "")
                    break_plz = False
                    for i in weapon_names:
                        if i.lower() in image_text.lower():
                            if weapon_name.lower() != i.lower():
                                break_plz = True
                    if break_plz == True:
                        continue
                    # print("parsing done")
                    con = sqlite3.connect("tc.db")
                    identifier_to_add = username + weapon_name + prefix_suffix + rawstat1 + rawstat2 + rawstat3 + rawnegstat
                    print(identifier_to_add)
                    if str(identifier_to_add) not in str(con.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier_to_add),)).fetchone())[2:-3]:
                        print("riven not seen before")
                        logging.info("before")
                        real_account = False
                        account_loop = 2
                        # print(username)
                        # real_account = True
                        while account_loop > 0:
                            account_info = is_account(username)
                            if account_info[0] == False:
                                username = username[:-1]
                            elif account_info[0] == True:
                                username = account_info[1]
                                account_loop = 0
                                real_account = True
                            account_loop -= 1
                            logging.info("each loop")
                        # print(username)
                        # print("after account loop")
                        if real_account == True:
                            logging.info("after")
                            buffered = BytesIO()
                            image_riven.save(buffered,format="JPEG")
                            image_riven = base64.b64encode(buffered.getvalue())
                            # print("encoded riven img")
                            #add riven to database
                            if chat_message != []:
                                con.execute(r"INSERT OR IGNORE INTO rivens (user, weapon, prefix, price, message, date, stat1stat, stat2stat, stat3stat, negstat, stat1val, stat2val, stat3val, negval, image, identifier, rawstat1, rawstat2, rawstat3, rawnegstat) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (username,weapon_name,prefix_suffix,price, str(chat_message[0]),str(todays_date), stat1stat, stat2stat, stat3stat,  negstat, stat1val, stat2val, stat3val, negval,  image_riven, identifier_to_add, rawstat1, rawstat2, rawstat3, rawnegstat))
                                con.commit()
                                print("into database")   
                                # ws.send("hoxxi smells")
                                # ws.send({"user":username,"weapon":weapon_name,"prefix":prefix_suffix,"price":price, "message":str(chat_message[0]),"date":str(todays_date), "first_stat":stat1stat, "second_stat":stat2stat, "third_stat":stat3stat,  "neg_stat":negstat, "first_stat_val":stat1val, "second_stat_val":stat2val, "third_stat_val":stat3val, "neg_val":negval,  "image":str(image_riven), "raw_stat1":rawstat1, "raw_stat2":rawstat2, "raw_stat3":rawstat3, "raw_negstat":rawnegstat})
                                # print("posted")
                            logging.info("should be in database")
                        else:
                            img1.save("fuck.png")
                            print("should have image saved")
                            continue
                except:
                    continue
    pyautogui.moveTo(1000, 1)
    ahk.click()
    # if hit_escape == False:
    #     ahk.send_input("{Esc}")
    # hit_escape = False
    # closed_chat()
    pyautogui.moveTo(950,550)
    ahk.send("{WheelDown 50}")
while 1:
    # closed_chat()
    tc_scraper()