#update-prices

import requests
import statistics
import json
import time


def second_function_i_dont_fucking_care(prices, prices_list, prices_dict):
    for price in prices['payload']['orders']:
        if price['order_type'] == "sell":
            if "mod_rank" in price:
                print(x)
                if price['mod_rank'] != 0:
                    continue            
            prices_list.append(price['platinum'])
            #sort and use cheapest 10 or so
    prices_list.sort()
    prices_list = prices_list[:9]
    try:
        avg = statistics.mean(prices_list)
    except:
        print(x, prices_list)
    try:
        median = statistics.median(prices_list)
    except:
        print(x, prices_list)
    prices_dict.update({x:{"avg":avg,"med":median}})

parts = requests.get("https://api.warframe.market/v1/items").json()

parts_list = []
for x in parts['payload']['items']:
    parts_list.append(x['url_name'])

prices_dict = {}
for x in parts_list:
    time.sleep(1)
    try:
        prices = requests.get("https://api.warframe.market/v1/items/" + x + "/orders").json()
    except:
        print(x)
    prices_list = []
    second_function_i_dont_fucking_care(prices, prices_list, prices_dict)


with open('data.txt', 'w') as data: 
     data.write(json.dumps(prices_dict))