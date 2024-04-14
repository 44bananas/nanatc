#tcclick_to_discord

from PIL import Image
import io
from dotenv import load_dotenv
import requests
import os
import discord
from discord import Color
from discord.ext import tasks
import json
import grading_functions
import bane_patch
import translator_search
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='tcclick_to_discord.log', filemode='a')

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

#function to send tc to discord
@tasks.loop()
async def tcapi_to_discord():
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
    logging.info("start")
    try:
        test = requests.get('local host ip for flask hosting db')
        data = test.json()
    except:
        logging.info("couldnt get data")
    logging.info("grabbed data")
    try:
        for x in data:
            logging.info("data loop start")
            #get the image
            data_found = eval(data[x]['image'])
            riven_image = Image.open(io.BytesIO(data_found))
            #get other stats
            user = data[x]['user']
            date = data[x]['date']
            price = data[x]['price']
            weapon = data[x]['weapon']
            tcmessage = data[x]['message']
            stat1stat = data[x]['first_stat']
            stat1val = str(bane_patch.front_to_back(stat1stat,data[x]['first_stat_val']))
            stat2stat = data[x]['second_stat']
            stat2val = str(bane_patch.front_to_back(stat2stat,data[x]['second_stat_val']))
            stat3stat = data[x]['third_stat']
            stat3val = str(bane_patch.front_to_back(stat3stat,data[x]['third_stat_val']))
            negstat = data[x]['neg_stat']
            negval = str(bane_patch.front_to_back(negstat,data[x]['neg_val']))
            logging.info("grabbed stats")
            #create the varriables for the stats
            prefix = data[x]['prefix']
            stats = [translator_search.translate_riven_tc(stat1stat), translator_search.translate_riven_tc(stat2stat), translator_search.translate_riven_tc(stat3stat)]
            logging.info("put stats into a list")
            #filters
            with open("filters.json") as json_file:
                filters = json.load(json_file)
            logging.info("opened filters")
            for filter in filters:
                logging.info("filter loop start")
                if str(data[x]['weapon']).replace("_"," ").lower() in filters[filter]['weapon'] or filters[filter]['weapon'] == "1" or (str(filters[filter]['weapon']).lower() == 'melee' and str(data[x]['weapon']).replace("_"," ").lower() in melee_dispos)or (str(filters[filter]['weapon']).lower() == 'shotgun' and str(data[x]['weapon']).replace("_"," ").lower() in shotgun_dispos)or (str(filters[filter]['weapon']).lower() == 'rifle' and str(data[x]['weapon']).replace("_"," ").lower() in rifle_dispos)or (str(filters[filter]['weapon']).lower() == 'archgun' and str(data[x]['weapon']).replace("_"," ").lower() in archgun_dispos)or (str(filters[filter]['weapon']).lower() == 'pistol' and str(data[x]['weapon']).replace("_"," ").lower() in pistol_dispos)or (str(filters[filter]['weapon']).lower() == 'kitgun' and str(data[x]['weapon']).replace("_"," ").lower() in kitgun_dispos):
                    logging.info("weapon match")
                    if sorted(stats) == sorted([filters[filter]['pos1'],filters[filter]['pos2'],filters[filter]['pos3']]):
                        logging.info("pos match")
                        if (negstat.lower() in str(filters[filter]['neg']).lower() and negstat != "") or str(filters[filter]['neg']).lower() == "['1']":
                            logging.info("neg match")                        
                            identifier_to_add = user + price + weapon + stat1stat + stat1val + stat2stat + stat2val + stat3stat + stat3val + negstat + negval
                            if str(identifier_to_add) not in str(identifiers):
                                logging.info("not seen already")
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
                                grades = grading_functions.get_varriants(weapon, stat1val, stat1stat, stat2val, stat2stat, stat3val, stat3stat, negval, negstat)
                                logging.info("graded")
                                if " " in user:
                                    description = "```/w \"" + user + "\" Hi, I'd like to buy your " + str(weapon).title() + " " + str(prefix).replace(weapon, "") + "```\n"
                                else:
                                    description = "```/w " + user + " Hi, I'd like to buy your " + str(weapon).title() + " " + str(prefix).replace(weapon, "") + "```\n"
                                stat1val, stat2val, stat3val, negval = str(bane_patch.back_to_front(stat1stat, stat1val)), str(bane_patch.back_to_front(stat2stat, stat2val)), str(bane_patch.back_to_front(stat3stat, stat3val)), str(bane_patch.back_to_front(negstat, -abs(float(negval))))
                                stat1stat, stat2stat, stat3stat, negstat = stat1stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "intial combo").replace("vs","to"), stat2stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "intial combo").replace("vs","to"), stat3stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "intial combo").replace("vs","to"), negstat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "intial combo").replace("vs","to")
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
                                    description += str(grades[z]['weapon']).title() + "\n" +pos1_color+ stat1stat+ " "+ stat1val+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ stat2val + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " + " \n"+pos3_color+ stat3stat+ " "+ stat3val+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " +" \n"+neg_color+ negstat+ " "+ negval + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")\n" + "\n"
                                logging.info("split grades")
                                # open the blacklist file
                                with open('blacklist.txt') as blacklist_file:
                                    for line in blacklist_file:
                                        line = line.replace('\n','')
                                        blacklist.append(line.lower())
                                riven_image.save("image.jpeg")
                                file = discord.File("image.jpeg", filename="image.jpeg")
                                if data[x]['user'].lower() not in str(blacklist).lower():
                                    channel = client.get_channel("snipe channel id here")
                                    embed = discord.Embed(title=weapon + " " + prefix.title() + " "+price, description=description, color=discord.Color.yellow())                                
                                    embed.set_author(name= data[x]['user'] + "\nFilter: " + filter)
                                    embed.set_thumbnail(url="attachment://image.jpeg")
                                    embed.set_footer(text="TC Message: " + tcmessage + "\n" +"seen at: " + date)
                                    message = await channel.send(embed=embed, file=file)
                                    logging.info("not blacklist " + str(identifier_to_add))
                                else:
                                    channel = client.get_channel("blacklist channel id here")
                                    embed = discord.Embed(title=weapon + " " + prefix.title() + " "+price, description= description, color=discord.Color.yellow())                                
                                    embed.set_author(name= data[x]['user'] + "\nFilter: " + filter)
                                    embed.set_thumbnail(url="attachment://image.jpeg")
                                    embed.set_footer(text="TC Message: " + tcmessage + "\n" +"Seen at: " + date)
                                    message = await channel.send(embed=embed, file=file)
                                    logging.info("blacklist " + str(identifier_to_add))
                                logging.info("end of loop")
    except:
        logging.info("no data in data")
            
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
