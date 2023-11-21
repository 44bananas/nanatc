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
    try:
        test = requests.get('http://ip of flask server goes here:5000/tc')
        data = test.json()
    except:
        print("couldnt get data")
    for x in data:
        #get the image
        data_found = eval(data[x]['image'])
        riven_image = Image.open(io.BytesIO(data_found))

        #get other stats
        user = data[x]['user'].replace("-","\-").replace("~","\~").replace("_","\_")
        date = data[x]['date']
        price = data[x]['price']
        weapon = data[x]['weapon']
        message = data[x]['message']
        stat1 = data[x]['first_stat']
        stat2 = data[x]['second_stat']
        stat3 = data[x]['third_stat']
        neg = data[x]['neg_stat']

        #open prefix_suffix
        with open("prefix_suffix.json") as json_file:
            prefix_suffix = json.load(json_file)
        #create the varriables for the stats
        prefix = data[x]['prefix']
        first_stat_name = ""
        second_stat_name = ""
        third_stat_name = ""
        #grab the stat names from the prefixes/suffix
        for i in prefix_suffix:
            if prefix_suffix[i]['prefix'].lower() in prefix.lower() and first_stat_name == "":
                first_stat_name = i.lower()
            elif prefix_suffix[i]['prefix'].lower() in prefix.lower() and second_stat_name == "":
                second_stat_name = i.lower()
            if prefix_suffix[i]['suffix'].lower() in prefix.lower() and third_stat_name == "":
                third_stat_name = i.lower()
        stats = [first_stat_name, second_stat_name, third_stat_name]
        #filters
        with open("filters.json") as json_file:
            filters = json.load(json_file)
        if neg != "":
            for filter in filters:
                if data[x]['weapon'].lower() == filters[filter]['weapon'].lower() or filters[filter]['weapon'].lower() == "1":
                    if sorted(stats) == sorted([filters[filter]['pos1'],filters[filter]['pos2'],filters[filter]['pos3']]):
                        identifier_to_add = user + price + weapon + stat1 + stat2 + stat3 + neg
                        if identifier_to_add not in identifiers:
                            identifiers.add(identifier_to_add)
                            #open the blacklist file
                            with open('blacklist.txt') as blacklist_file:
                                for line in blacklist_file:
                                    line = line.replace('\n','')
                                    blacklist.append(line.lower())
                            riven_image.save("image.jpeg")
                            file = discord.File("image.jpeg", filename="image.jpeg")
                            if data[x]['user'].lower() not in str(blacklist).lower():
                                channel = client.get_channel(snipe_channel_id)
                                embed = discord.Embed(title=weapon + " " + prefix.title() + " "+price, description= "\n /w " + user + " hi could you please link " + weapon + " " + prefix + "\n\n**" + stat1 + "\n" + stat2 + "\n" + stat3 + "\n"+ neg +"**" + "\n\nMessage:\n```" + message + "```", color=discord.Color.yellow())
                                embed.set_author(name= data[x]['user'])
                                embed.set_image(url="attachment://image.jpeg")
                                message = await channel.send(embed=embed, file=file)
                            else:
                                channel = client.get_channel(bl_channel_id)
                                embed = discord.Embed(title=weapon + " " + prefix.title() + " "+price, description= "\n /w " + user + " hi could you please link " + weapon + " " + prefix + "\n\n**" + stat1 + "\n" + stat2 + "\n" + stat3 + "\n"+ neg +"**" + "\n\nMessage:\n```" + message + "```", color=discord.Color.yellow())
                                embed.set_author(name= data[x]['user'])
                                embed.set_image(url="attachment://image.jpeg")
                                message = await channel.send(embed=embed, file=file)
            
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
