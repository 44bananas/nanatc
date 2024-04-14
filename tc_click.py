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
import io
import base64
from io import BytesIO

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='tc_click.log', filemode='a')
ahk = AHK(executable_path='ahk path here')
file = open("ee.log path here")
file.seek(0, io.SEEK_END)

time.sleep(5)

#varrs needed
prefix_suffix_list = ['Laci','Nus','Ampi','Bin','Argi','Con','Pura','Ada','Manti','Tron','Geli','Do','Toxi','Tox','Igni','Pha','Vexi','Tio','Crita','Cron','Pleci','Nent','Acri','Tis','Visi','Ata','Exi','Cta','Croni','Dra','Conci','Nak','Para','Um','Magna','Ton','Insi','Cak','Sci','Sus','Arma','Tin','Forti','Us','Sati','Can','Lexi','Nok','Feva','Tak','Locti','Tor','Hexa','Dex','Deci','Des','Zeti','Mag','Hera','Lis','Tempi','Nem']
stat_names = ["Additional Combo Count Chance","Chance to Gain Combo Count","Fire Rate","Fire Rate(x2 for Bows)","Attack Speed","Ammo Maximum","Damage to Corpus","Damage to Grineer","Damage to Infested","Cold","Combo Duration","Critical Chance","Critical Chance (x2 for Heavy Attacks)","Critical Chance for Slide attack","Critical Damage","Damage","Melee damage","Electricity","Heat","Punch Through","Finisher Damage","Projectile Speed","Initial Combo","Impact","Magazine Capacity","Heavy Attack Efficiency","Multishot","Status Chance","Toxin","Puncture","Reload Speed","Range","Slash","Status Duration","Weapon Recoil","Zoom"]

#open dispos
with open("rifle_dispos.txt") as json_file:
    rifle_dispos = json.load(json_file)
with open("pistol_dispos.txt") as json_file:
    pistol_dispos = json.load(json_file)
with open("melee_dispos.txt") as json_file:
    melee_dispos = json.load(json_file)
with open("shotgun_dispos.txt") as json_file:
    shotgun_dispos = json.load(json_file)
with open("archgun_dispos.txt") as json_file:
    archgun_dispos = json.load(json_file)
with open("kitgun_dispos.txt") as json_file:
    kitgun_dispos = json.load(json_file)

weapon_names = {}
for x in [shotgun_dispos, melee_dispos, rifle_dispos, archgun_dispos, pistol_dispos,kitgun_dispos]:
    weapon_names.update(x)

def find_match(stat):
    for stats in stat_names:
        if Levenshtein.jaro_winkler(stat.lower(), stats.lower()) > 0.894:
            if "heavy" in stats.lower() and "slide" in stat.lower():
                continue
            return stats
    if stat.lower() == "almpact":
        return "Impact"
    if stat.lower() == "3kcold":
        return "Cold"
    if stat.lower() == "3 cold":
        return "Cold"
    return stat
ready_to_check = False

def is_account(ign):
    xbox = "**removed private url**"
    psn = "**removed private url**"
    pc = "**removed private url**"
    url = "**removed private url**"
    logging.info("before requests")
    data = grequests.map(grequests.get(u) for u in [pc + url + ign, psn + url + ign, xbox + url + ign])
    logging.info("after requests")
    is_account_real = False
    for i in data:
        try:
            if "Retry PC account:" in i.text:
                is_account_real = True
            elif i.status_code == 400 or i.status_code == 409:
                continue
            else:
                is_account_real = True
        except:
            is_account_real = False
            logging.info("account check failed")
    return is_account_real

def ocr_error(stats):
    stats = stats.strip()
    if stats[0] ==".":
        stats = stats[1:]
    if stats[0] =="%":
        stats = stats[1:]
    return stats

def closed_chat():  
    img2 = ImageGrab.grab(bbox=(250, 670, 500, 750))
    #turn image to data
    img_loc2 = pytesseract.image_to_data(img2, output_type=Output.DICT, config="--psm 6 -c preserve_interword_spaces=1 -c tessedit_char_whitelist=' []01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-.:'")
    if "options" in str(img_loc2['text']).lower():
        logging.info("T")
        pyautogui.moveTo(1380,530)
        ahk.click()
        ahk.send("T")
        
def tc_scraper():
    closed_chat()
    todays_date = time.time()
    #take a ss of tc
    #(left_x, top_y, right_x, bottom_y)
    left_x = 0
    top_y = 950
    right_x = 1420
    bottom_y = 1030
    #scroll up
    pyautogui.moveTo(1380,530)
    ahk.send("{WheelUp 3}")
    time.sleep(0.2)
    img1 = ImageGrab.grab(bbox=(left_x, top_y, right_x, bottom_y))
    #left, bottom, right, top
    #turn image to data
    img_loc = pytesseract.image_to_data(img1, output_type=Output.DICT, config="--psm 6 -c preserve_interword_spaces=1 -c tessedit_char_whitelist=' []01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-.:'")
    logging.info("turn tc ss into text")
    #create a tc message out of the data
    tc_message = "".join(img_loc['text'])
    #split them into each message
    text_split = [message for message in re.findall("[\s\S]*?(?=\[[0-9]{2}\:[0-9]{2}\])",tc_message) if message.strip().lower()]
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
        prefix_suffix = re.sub("\].*","",re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-1].lower())).strip()
        chat_message = [message.strip() for message in text_split if weapon_name in message.lower() and prefix_suffix in message.lower()]
        if any(weapon.lower() in weapon_name for weapon in weapon_names):
            weapon_name = [weapon for weapon in weapon_names if weapon.lower() in weapon_name][0]
        else:
            continue
        username = re.sub("[\[\]\']","",str(re.findall("(?<=\[[0-9]{2}\:[0-9]{2}\])(.*?)(?=:)",str(chat_message)))).strip()
        #to get price
        try:
            prices = [re.sub("[\[{].*?[\]|}]", " ",i) for i in re.findall("[\[{].*?[\]|}] *\d*[.,]?\d*k?p?w?",str(chat_message).lower())]
            links = re.findall("[\[{].*?[\]|}]",str(chat_message).lower())
            price = prices[links.index(link.replace(" ","").lower())]
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
                ready_to_check = True
                #click
                time.sleep(0.5)
                line = file.readlines()
                ahk.click()
                time.sleep(2)
                logging.info("ready to check")
                if ready_to_check == True:
                    line = file.readlines()
                    line = "".join(line)
                    if "(/Lotus/Upgrades" in line:
                        logging.info("sees that theres a riven")
                        if any(single_line for single_line in line.splitlines() if ("Resource load completed" in single_line) and ("(/Lotus/Upgrades" in single_line)):      
                            logging.info("riven fast")                  
                            if ImageGrab.grab(bbox=(820, 350, 1100, 780)).getpixel((28,27)) == (193, 188, 232):
                                #move cursor out of the way
                                pyautogui.moveTo(1000, 1)
                                #take ss
                                image_riven = ImageGrab.grab(bbox=(820, 350, 1100, 735))
                            ahk.send_input("{Esc}")
                            logging.info("escaped first")
                            closed_chat()
                            ready_to_check = False        
                        else:
                            logging.info("riven slow")
                            read_count = 10
                            while ready_to_check == True:
                                line = line.join(file.readlines())
                                if ("Resource load completed" in line) and ("(/Lotus/Upgrades" in line):
                                    if ImageGrab.grab(bbox=(820, 350, 1100, 780)).getpixel((28,27)) == (193, 188, 232):
                                        #move cursor out of the way
                                        pyautogui.moveTo(1000, 1)
                                        #take ss
                                        image_riven = ImageGrab.grab(bbox=(820, 350, 1100, 735))
                                    ahk.send_input("{Esc}")
                                    logging.info("escaped second")
                                    ready_to_check = False   
                                    closed_chat()   
                                elif read_count == 0:
                                    ahk.send_input("{Esc}")
                                    logging.info("escaped on read count")
                                    logging.info("read count ran out")
                                    ready_to_check = False    
                                    closed_chat()                                    
                                read_count -= 1                    
                    else:
                        logging.info("no riven")                        
                        ahk.send_input("{Esc}")
                        logging.info("escaped third")
                        ready_to_check = False
                        closed_chat()                                           
                else:
                    left_pos = ""
                    top_pos = ""
                    ready_to_check = False
                    closed_chat()
                    continue
                closed_chat()
                left_pos = ""
                top_pos = ""
                try:
                    image_text = re.sub("[^A-Za-z0-9\+\-%()\n .]","",pytesseract.image_to_string(image_riven.crop((30, 100, 245, 310)))).strip()
                except:
                    pyautogui.moveTo(1380,530)
                    ahk.send("{WheelDown 50}")
                    ready_to_check = False
                    continue
                if "".join(re.findall("[a-z]*",weapon_name.lower())) not in "".join(re.findall("[a-z]*","".join(image_text).lower())) or "".join(re.findall("[a-z]*",prefix_suffix.lower())) not in "".join(re.findall("[a-z]*","".join(image_text).lower())):
                    logging.info("leftover " + "".join(image_text).lower())
                    logging.info("weapon " + str(weapon_name))
                    logging.info("link" + str(link))
                    continue
                logging.info("read riven")
                try:
                    image_text = weapon_name + image_text.lower().split(weapon_name)[1]
                except:
                    image_text = image_text                       
                #remove weapon name
                image_text = [i for i in image_text.replace(weapon_name.lower(), "").splitlines() if i != ""]
                try:
                #remove prefix name
                    if image_text[0].lower().strip() == prefix_suffix:
                        image_text = image_text[1:]
                    elif image_text[0].lower().strip() + image_text[1].lower().strip() == prefix_suffix:
                        image_text = image_text[2:]
                except:
                    logging.info("failed to remove prefix name")
                    continue
                # assign stats to varriables
                rawnegstat, rawstat1, rawstat2, rawstat3, stat1stat, stat1val, stat2stat, stat2val, stat3stat, stat3val, negstat, negval = "", "", "", "", "", "", "", "", "", "", "", ""
                #negstat
                if "recoil" in image_text[-1].lower():
                    if "-" in image_text[-1]:
                        rawnegstat = ""
                    if "+" in image_text[-1]:
                        rawnegstat = image_text[-1]
                        image_text.remove(image_text[-1])
                elif bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1].lower() and ("-" in image_text[-1] or (bool(re.search(r'[x]\d+\.\d+', image_text[-1].lower())) and  bool(bane in image_text[-1].lower() for bane in ["corpus","grineer","infested"]))):
                    rawnegstat = image_text[-1]
                    image_text.remove(image_text[-1])
                elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True and ( "-" in image_text[-1] or (bool(re.search(r'[x]\d+\.\d+', image_text[-1].lower())) and  bool(bane in image_text[-1].lower() for bane in ["corpus","grineer","infested"]))):
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
                    if "-" in rawstat1 and "recoil" not in rawstat1:
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
                    if "-" in rawstat2 and "recoil" not in rawstat2:
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
                    if "-" in rawstat3 and "recoil" not in rawstat3:
                        rawstat3 = ""
                except:
                    rawstat3 = ""
                    logging.info("no stat 3 or stat 3 break")
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
                    stat1val = re.findall("\-*\d+\.*\d*",stat1.split(" ")[0])[0]
                    stat1stat = " ".join(stat1.split(" ")[1:])
                except:
                    stat1val = ""
                    stat1stat = ""
                    logging.info("stat1 failed")
                try:
                    stat2val = re.findall("\-*\d+\.*\d*",stat2.split(" ")[0])[0]
                    stat2stat = " ".join(stat2.split(" ")[1:])
                except:
                    stat2val = ""
                    stat2stat = ""
                    logging.info("stat2 failed")
                try:
                    stat3val = re.findall("\-*\d+\.*\d*",stat3.split(" ")[0])[0]
                    stat3stat = " ".join(stat3.split(" ")[1:])
                except:
                    stat3val = ""
                    stat3stat = ""
                    logging.info("stat3 failed")
                try:
                    negval = re.findall("\-*\d+\.*\d*",negstat.split(" ")[0])[0]
                    negstat = " ".join(negstat.split(" ")[1:])
                except:
                    negval = ""
                    negstat = ""
                    logging.info("negstat failed")                
                logging.info("parse info from riven image")
                #identifier to reduce duplication
                con = sqlite3.connect("tc.db")
                stat1stat = find_match(stat1stat)
                stat2stat = find_match(stat2stat)
                stat3stat = find_match(stat3stat)
                negstat = find_match(negstat)
                identifier_to_add = username + weapon_name + prefix_suffix + rawstat1 + rawstat2 + rawstat3 + rawnegstat
                if str(identifier_to_add) not in str(con.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier_to_add),)).fetchone())[2:-3]:
                    logging.info("before")
                    real_account = False
                    account_loop = 2
                    while account_loop > 0:
                        if is_account(username) == False:
                            username = username[:-1]
                        elif is_account(username) == True:
                            account_loop = 0
                            real_account = True
                        account_loop -= 1
                        logging.info("each loop")
                    if real_account == True:
                        logging.info("after")
                        logging.info(stat1stat, stat1val, " stat1\n",stat2stat, stat2val," stat2\n", stat3stat, stat3val, " stat3\n",negstat, negval, " neg\n\n")
                        logging.info(weapon_name, " ", prefix_suffix)
                        buffered = BytesIO()
                        image_riven.save(buffered,format="JPEG")
                        image_riven = base64.b64encode(buffered.getvalue())
                        #add riven to database
                        if chat_message != []:
                            con.execute("INSERT OR IGNORE INTO rivens (user, weapon, prefix, price, message, date, stat1stat, stat2stat, stat3stat, negstat, stat1val, stat2val, stat3val, negval, image, identifier, rawstat1, rawstat2, rawstat3, rawnegstat) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (username,weapon_name,prefix_suffix,price, str(chat_message[0]),str(todays_date), stat1stat, stat2stat, stat3stat,  negstat, stat1val, stat2val, stat3val, negval,  image_riven, identifier_to_add, rawstat1, rawstat2, rawstat3, rawnegstat))
                            con.commit()
                        logging.info("should be in database")
    pyautogui.moveTo(1380,530)
    ahk.send("{WheelDown 50}")
while 1:
    closed_chat()
    tc_scraper()
