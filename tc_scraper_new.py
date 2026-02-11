import grequests
from dotenv import load_dotenv
import os
import discord
from discord import Color
from discord.ext import tasks
import json
from PIL import Image
import io
import translator_search
import grader
import bane_patch

#load the discord token and id
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#declare discord intents
intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents = intents)

#varrs needed
identifiers = set()
blacklist = []

def description_creation(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negname, prefix, description):
    grades = grader.grade(str(weapon), str(stat1val), str(stat1name).replace("_", " "), str(stat2val), str(stat2name).replace("_", " "), str(stat3val), str(stat3name).replace("_", " "), str(negval), str(negname).replace("_", " "), "8")    
    description += "Grades for " +  weapon.title() + " " +  prefix + "\n"
    empty_description = description
    stat1val, stat2val, stat3val, negval = bane_patch.back_to_front(stat1name, stat1val), bane_patch.back_to_front(stat2name, stat2val), bane_patch.back_to_front(stat3name, stat3val), bane_patch.back_to_front(negname, -abs(float(negval)))
    stat1stat, stat2stat, stat3stat, negstat = stat1name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat2name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat3name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), negname.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo")
    for z in grades:
        if "?" in str(grades[z]) or "circle" not in str(grades[z]):
            continue
        try:
            pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
        except:
            pos1_color, pos_grade1_1, pos_grade1_2  = "", "", ""
        try:
            pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
        except:
            pos2_color, pos_grade2_1, pos_grade2_2 = "", "", ""
        try:
            pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
        except:
            pos3_color, pos_grade3_1, pos_grade3_2 = "", "", ""
        try:
            neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
        except:
            neg_color, neg_grade1, neg_grade2 = "", "", ""
        wiki_url = "https://warframe.fandom.com/wiki/"
        weapon_url = str(grades[z]['weapon']).title().replace(" ","_").replace("And","&")
        if "mk" in weapon_url.lower():
            weapon_url = wiki_url + "MK" +(weapon_url[2:]).title()
        else:
            weapon_url = wiki_url + weapon_url        
        description += "["+str(grades[z]['weapon']).title() + "]("+ weapon_url+")\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
        if stat3stat != "[]":
            description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
        if negstat != "[]":
            description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
        description += "\n\n"
    if description != empty_description:
        return description
    else:
        for z in grades:
            try:
                pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
            except:
                pos1_color, pos_grade1_1, pos_grade1_2  = "", "", ""
            try:
                pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
            except:
                pos2_color, pos_grade2_1, pos_grade2_2 = "", "", ""
            try:
                pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
            except:
                pos3_color, pos_grade3_1, pos_grade3_2 = "", "", ""
            try:
                neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
            except:
                neg_color, neg_grade1, neg_grade2 = "", "", ""
            wiki_url = "https://warframe.fandom.com/wiki/"
            weapon_url = str(grades[z]['weapon']).title().replace(" ","_").replace("And","&")
            if "mk" in weapon_url.lower():
                weapon_url = wiki_url + "MK" +(weapon_url[2:]).title()
            else:
                weapon_url = wiki_url + weapon_url            
            description += "["+str(grades[z]['weapon']).title() + "]("+ weapon_url+")\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
            if "[]" not in stat3stat:
                description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
            if "[]" not in negstat:
                description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
            description += "\n\n"
        return description

#function to send tc to discord
@tasks.loop()
async def tcapi_to_discord():
    weapon_names = []
    with open("weapon_info.json") as json_file:
            weapon_info = json.load(json_file)
    for item in weapon_info:
        for weapons in weapon_info[item]['variants'].items():
            weapon_names.append(weapons[0].replace("Primary","").replace("Secondary","").strip())
    try:
        url = ["http://10.0.0.61:5000/tc"]
        rawdata = grequests.map(grequests.get(u) for u in url)
    except:
        print("couldnt get data")
    try:
        for data in rawdata:
            try:
                data = dict(json.loads(data.text))
            except:
                print("data fucked")
            for riven in data:
                #get the image
                data_found = eval(data[riven]['image'])
                riven_image = Image.open(io.BytesIO(data_found))
                #get other stats
                user = data[riven]['user']
                date = data[riven]['date']
                price = data[riven]['price']
                weapon = data[riven]['weapon']
                tcmessage = data[riven]['message']
                stat1stat = translator_search.translate_riven_tc(data[riven]['first_stat'])            
                stat2stat = translator_search.translate_riven_tc(data[riven]['second_stat'])            
                stat3stat = translator_search.translate_riven_tc(data[riven]['third_stat'])            
                negstat = translator_search.translate_riven_tc(data[riven]['neg_stat'])
                stat1val = str(bane_patch.front_to_back(stat1stat,data[riven]['first_stat_val']))
                stat2val = str(bane_patch.front_to_back(stat2stat,data[riven]['second_stat_val']))
                stat3val = str(bane_patch.front_to_back(stat3stat,data[riven]['third_stat_val']))
                negval = str(bane_patch.front_to_back(negstat,data[riven]['neg_val']))
                #create the varriables for the stats
                prefix = data[riven]['prefix']
                stats = [stat1stat, stat2stat, stat3stat]
                #filters
                with open("filters.json") as json_file:
                    filters = json.load(json_file)
                for filter in filters:
                    for item in weapon_info:
                        if str(data[riven]['weapon']).replace("_"," ").title() in weapon_names:
                            if str(data[riven]['weapon']).replace("_"," ").lower() in filters[filter]['weapon'] or filters[filter]['weapon'] == "1" or filters[filter]['weapon'] == "any" or (str(filters[filter]['weapon']).lower() == weapon_info[item]['type']):
                                if sorted(stats) == sorted([filters[filter]['pos1'],filters[filter]['pos2'],filters[filter]['pos3']]):
                                    if (negstat.lower() in str(filters[filter]['neg']).lower() and negstat != "") or str(filters[filter]['neg']).lower() == "['1']":                     
                                        identifier_to_add = user + price + weapon + stat1stat + stat1val + stat2stat + stat2val + stat3stat + stat3val + negstat + negval
                                        if str(identifier_to_add) not in str(identifiers):
                                            identifiers.add(identifier_to_add)
                                            if stat1val == "":
                                                stat1val = "0"
                                            if stat2val == "":
                                                stat2val = "0"
                                            if stat3val == "":
                                                stat3val = "0"
                                            if negval == "":
                                                negval = "0"                                
                                            stat1stat, stat2stat, stat3stat, negstat = translator_search.translate_riven_tc(stat1stat), translator_search.translate_riven_tc(stat2stat), translator_search.translate_riven_tc(stat3stat), translator_search.translate_riven_tc(negstat)
                                            if " " in user:
                                                description = "```/w \"" + user + "\" Hi, I'd like to buy your " + str(weapon).title() + " " + str(prefix).replace(weapon, "") + "```\n"
                                            else:
                                                description = "```/w " + user + " Hi, I'd like to buy your " + str(weapon).title() + " " + str(prefix).replace(weapon, "") + "```\n"
                                            description = description_creation(weapon, abs(float(stat1val)), stat1stat, abs(float(stat2val)), stat2stat, abs(float(stat3val)), stat3stat, abs(float(negval)), negstat, prefix,  description)
                                            # open the blacklist file
                                            with open('blacklist.txt') as blacklist_file:
                                                for line in blacklist_file:
                                                    line = line.replace('\n','')
                                                    blacklist.append(line.lower())
                                            riven_image.save("image.jpeg")
                                            file = discord.File("image.jpeg", filename="image.jpeg")
                                            if data[riven]['user'].lower() not in str(blacklist).lower():
                                                channel = client.get_channel(1278168660115980319)
                                                embed = discord.Embed(title=weapon + " " + prefix.title() + " "+price, description=description, color=discord.Color.yellow())                                
                                                embed.set_author(name= data[riven]['user'] + "\nFilter: " + filter)
                                                embed.set_image(url="attachment://image.jpeg")
                                                embed.set_footer(text="TC Message: " + tcmessage + "\n" +"seen at: " + date)
                                                message = await channel.send(embed=embed, file=file)
                                                break
                                            else:
                                                channel = client.get_channel(1278168697034506290)
                                                embed = discord.Embed(title=weapon + " " + prefix.title() + " "+price, description= description, color=discord.Color.yellow())                                
                                                embed.set_author(name= data[riven]['user'] + "\nFilter: " + filter)
                                                embed.set_image(url="attachment://image.jpeg")
                                                embed.set_footer(text="TC Message: " + tcmessage + "\n" +"Seen at: " + date)
                                                message = await channel.send(embed=embed, file=file)
                                                break
    except:
        print("no data in data")
            
#start the bot loop
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} has connectred to Discord!'
        f'{guild.name}(id: {guild.id})'
    )
    tcapi_to_discord.start()
client.run(TOKEN)
