#tc_click

# from time import time
import pytesseract
from pytesseract import Output
import PIL.ImageGrab as ImageGrab
import re
import json
import pyautogui
import time
import sqlite3
import base64
from io import BytesIO
from ahk import AHK
ahk = AHK(executable_path='path\\tc_clicking\\AutoHotkey\\AutoHotkey.exe')

#varrs needed
identifier = set()
count = 0
prefix_suffix_list = ['Laci','Nus','Ampi','Bin','Argi','Con','Pura','Ada','Manti','Tron','Geli','Do','Toxi','Tox','Igni','Pha','Vexi','Tio','Crita','Cron','Pleci','Nent','Acri','Tis','Visi','Ata','Exi','Cta','Croni','Dra','Conci','Nak','Para','Um','Magna','Ton','Insi','Cak','Sci','Sus','Arma','Tin','Forti','Us','Sati','Can','Lexi','Nok','Feva','Tak','Locti','Tor','Hexa','Dex','Deci','Des','Zeti','Mag','Hera','Lis','Tempi','Nem']
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
kitgun_dispos = ["catchmoon",'vermisplicer','rattleguts','sporelacer','gaze','tombfinger']

def hitescifpurbl():
    #reset
    if ImageGrab.grab(bbox=(820, 350, 1100, 780)).getpixel((28,27)) == (193, 188, 232):
        ahk.send_input("{Esc}")

def tc_scraper():
    hitescifpurbl()
    global identifier
    global count
    todays_date = time.time()
    tc_message = " "
    #take a ss of tc
    #(left_x, top_y, right_x, bottom_y)
    left_x = 0
    top_y = 900
    right_x = 1420
    bottom_y = 1030
    #scroll up
    pyautogui.moveTo(1380,530)
    ahk.send("{WheelUp 3}")
    #give time for riven to load
    time.sleep(0.5)
    img1 = ImageGrab.grab(bbox=(left_x, top_y, right_x, bottom_y))
    #left, bottom, right, top
    #turn image to data
    img_loc = pytesseract.image_to_data(img1, output_type=Output.DICT)
    #create a tc message out of the data
    tc_message = tc_message.join(img_loc['text'])
    #split them into each message
    text_split = [message for message in re.findall("[\s\S]*?(?=\[[0-9]{2}\:[0-9]{2}\])",tc_message) if message.strip().lower()]
    left_pos = ""
    top_pos = ""
    #loop through the data
    for x in range(len(img_loc['level'])):
        try:
            #weapon name
            weapon_name_loop_count = 2
            weapon_name = re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-1].lower())
            while str(weapon_name)[0] != "[" and weapon_name != "":
                # weapon_name = re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc[x-weapon_name_loop_count].lower()) + " " + weapon_name
                if "[" in re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-weapon_name_loop_count].lower()):
                    weapon_name =  re.sub(r'.*\[', "", re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-weapon_name_loop_count].lower())) + " " + weapon_name
                    weapon_name = "[" + weapon_name
                else:
                    weapon_name =  re.sub(r'.*\[', "", re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-weapon_name_loop_count].lower())) + " " + weapon_name
                weapon_name_loop_count += 1
            if (weapon_name[0] != "[" and weapon_name[-1] != "]") or weapon_name == '[]' or weapon_name[-1] != "]":
                continue
            link = weapon_name
            weapon_name = weapon_name.replace(re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-1].lower()),"").replace("[","").lower().strip().replace("&", "and")
            #riven prefix name, chat message and username
            prefix_suffix = re.sub("\].*","",re.sub(r'[^A-Za-z&\[\]\-]', '',img_loc['text'][x-1].lower())).strip()
            chat_message = [message.strip() for message in text_split if weapon_name in message.lower() and prefix_suffix in message.lower()]
            username = re.sub("[\[\]\']","",str(re.findall("(?<=\[[0-9]{2}\:[0-9]{2}\])(.*?)(?=:)",str(chat_message)))).strip()
            #to get price
            try:
                prices = [re.sub("[\[{].*?[\]|}]", " ",i) for i in re.findall("[\[{].*?[\]|}] *\d*[.,]?\d*k?p?w?",str(chat_message).lower())]
                links = re.findall("[\[{].*?[\]|}]",str(chat_message).lower())
                price = prices[links.index(link)]
            except:
                price = ""
            # if the chat message isnt empty
            if chat_message != []:
                #check if riven name is in it
                if any(suffix.lower() in prefix_suffix for suffix in prefix_suffix_list) and prefix_suffix.lower() != "mag":
                    # cheack if its a weapon
                    if any(weapon.lower() in weapon_name for weapon in rifle_dispos) or any(weapon.lower() in weapon_name for weapon in shotgun_dispos) or any(weapon.lower() in weapon_name for weapon in pistol_dispos) or any(weapon.lower() in weapon_name for weapon in kitgun_dispos) or any(weapon.lower() in weapon_name for weapon in melee_dispos) or any(weapon.lower() in weapon_name for weapon in archgun_dispos):
                        #move cursor to where riven name is
                        if left_pos == "" and top_pos == "":
                            left_pos = img_loc['left'][x-1] + left_x
                            top_pos = top_y + img_loc['top'][x-1]
                            bottom_pos = top_pos + img_loc['height'][x-1]
                            right_pos = left_pos + img_loc['width'][x-1]
                            xcenter = (left_pos + right_pos) /2
                            ycenter = (top_pos + bottom_pos) /2
                        print(xcenter, ycenter)
                        pyautogui.moveTo(xcenter, ycenter)
                        print(chat_message)
                        print(weapon_name)
                        print(prefix_suffix)
                        #click
                        ahk.click()
                        #move cursor out of the way
                        pyautogui.moveTo(1000, 1)
                        #time to let riven load
                        time.sleep(0.4)
                        #read the riven
                        if ImageGrab.grab(bbox=(820, 350, 1100, 780)).getpixel((28,27)) == (193, 188, 232):
                            # print("sees riven")
                            image_riven = ImageGrab.grab(bbox=(820, 350, 1100, 735))
                            image_text = re.sub("[^A-Za-z0-9\+\-%()\n .]","",pytesseract.image_to_string(image_riven.crop((30, 100, 245, 310)))).strip()
                            ahk.send_input("{Esc}")
                            try:
                                image_text = weapon_name + image_text.lower().split(weapon_name)[1]
                            except:
                                image_text = image_text                            
                            #remove weapon name
                            image_text = image_text.replace(weapon_name.lower(), "").splitlines()
                            #remove prefix name
                            if image_text[0].lower().strip() == prefix_suffix:
                                image_text = image_text[1:]
                            elif image_text[0].lower().strip() + image_text[1].lower().strip() == prefix_suffix:
                                image_text = image_text[2:]
                            #assign stats to varriables
                            #negstat
                            if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
                                negstat = image_text[-1]
                                image_text.remove(image_text[-1])
                            elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                                negstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                                image_text.remove(image_text[-1])
                                image_text.remove(image_text[-1])
                            if "+" in negstat and "recoil" not in negstat:
                                negstat = ""
                            #stat1
                            try:
                                if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
                                    stat1 = image_text[-1]
                                    image_text.remove(image_text[-1])
                                elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                                    stat1 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                                    image_text.remove(image_text[-1])
                                    image_text.remove(image_text[-1])
                                if "-" in stat1 and "recoil" not in stat1:
                                    stat1 = ""
                            except:
                                stat1 = ""
                                print("stat 1 break")
                            #stat2
                            try:
                                if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
                                    stat2 = image_text[-1]
                                    image_text.remove(image_text[-1])
                                elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                                    stat2 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                                    image_text.remove(image_text[-1])
                                    image_text.remove(image_text[-1])
                                if "-" in stat2 and "recoil" not in stat2:
                                    stat2 = ""
                            except:
                                stat2 = ""
                                print("stat 2 break")
                            try:
                                if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
                                    stat3 = image_text[-1].replace("[","").replace("]","")
                                    image_text.remove(image_text[-1])
                                elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
                                    stat3 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
                                    image_text.remove(image_text[-1])
                                    image_text.remove(image_text[-1])
                                if "-" in stat3 and "recoil" not in stat3:
                                    stat3 = ""
                            except:
                                stat3 = ""
                                print("no stat 3 or stat 3 break")
                            #identifier to reduce duplication
                            identifier_to_add = username + weapon_name + prefix_suffix + stat1 + stat2 + stat3 + negstat 
                            if identifier_to_add not in identifier:
                                if image_text == []:
                                    buffered = BytesIO()
                                    image_riven.save(buffered,format="JPEG")
                                    image_riven = base64.b64encode(buffered.getvalue())
                                    #add riven to database
                                    con = sqlite3.connect("tc.db")
                                    print(image_text)
                                    print(weapon_name," ", prefix_suffix, " ", username, " ", price, "\n\n")
                                    print(stat1, stat2, stat3, negstat)
                                    print(type(username),type(weapon_name),type(prefix_suffix),type(price),type(chat_message),type(todays_date),type(stat1),type(stat2),type(stat3),type(negstat),type(identifier_to_add))
                                    con.execute("INSERT OR IGNORE INTO rivens (user, weapon, prefix, price, message, date, stat1, stat2, stat3, neg, image, identifier) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (username,weapon_name,prefix_suffix,price, str(chat_message[0]),str(todays_date), stat1, stat2, stat3,  negstat, image_riven, identifier_to_add))
                                    con.commit()
                                    print("should be in database")
                        else:
                            left_pos = ""
                            top_pos = ""
                            continue
                        try:
                            identifier.add(identifier_to_add)
                        except:
                            identifier_to_add = ""
                        count += 1
                        left_pos = ""
                        top_pos = ""
        except:
            continue
    # scroll down
    pyautogui.moveTo(1380,530)
    ahk.send("{WheelDown 10}")
    print("looped")

time.sleep(5)
while True:
    tc_scraper()