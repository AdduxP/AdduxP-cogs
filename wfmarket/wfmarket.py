import discord
from discord.ext import commands
from datetime import datetime
import requests

class Wfmarket:
    """Warframe commands for """

    def __init__(self, bot):
        self.bot = bot
        reload_items()

    @commands.command(name="refreshtrades")
    async def reload(self):
        """Refresh the traded items list!"""
        reload_items()
        await self.bot.say("Trade items have been reloaded!")

    @commands.command(pass_context=True, name="price", aliases=['pc', 'pricecheck'])
    async def pricecheck(self, context, *, item: str):
        """Refresh the traded items list!"""
        print(item)
        lowest = get_lowest_offer(item)
        avg = get_average_offer(item)


        avg_price = avg[0]
        avg_num_offers = avg[1]
        lowest_price = lowest.price
        lowest_seller = lowest.ign

        reply = "*Average Price*: **{}p** from *{}* online offers \n*Lowest Available Price*: **{}p** from *{}*".format(avg_price,
                                                    avg_num_offers, lowest_price, lowest_seller)
        await self.bot.say(reply)


class Itemlist():
    def __init__(self, data):
        self.itemname       = data['item_name']
        self.itemtype       = data['item_type']

    def name(self):
        return self.itemname.lower()

    def type(self):
        return self.itemtype.lower()

class Order():
    def __init__(self, data):
        self.ign            = data['ingame_name']
        self.online         = data['online_ingame']
        self.price          = data['price']

    def __str__(self):
        return '{}: {}'.format(self.ign, self.price)
    def __repr__(self):
        return '{}: {}'.format(self.ign, self.price)


itemlist = {}

def reload_items():
    lookup_data = None
    r = None
    url = 'http://warframe.market/api/get_all_items_v2'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise RuntimeError('Error while connecting to ' + url)

    # Raise an exception in case of a bad response
    if not r.status_code == requests.codes.ok:
        raise RuntimeError('Bad response from ' + url)

    # Response.json() might raise ValueError
    try:
        lookup_data = r.json()
    except ValueError as e:
        raise RuntimeError('Bad JSON from ' + url) from e

    # Raise an exception in case of an empty response
    if not lookup_data:
        raise RuntimeError('Empty response from ' + url)

    for d in lookup_data:
        item = Itemlist(d)
        itemlist[item.name()] = item.type()

def lookup_item(query):
    try:
        itemtype = itemlist[query.lower()]
    except KeyError as e:
        itemtype = None

    return itemtype

def get_item_orders(item):
    itemtype = lookup_item(item)
    if not itemtype or itemtype == 'void relic':
        return None

    revisedTypeName = itemtype.title()
    revisedItemName = item.title()
    revisedItemName = revisedItemName.replace(" ", "%20")
    url = 'http://warframe.market/api/get_orders/' + revisedTypeName + '/' + revisedItemName
    return url


#what if nobody's online?
#what if there are no sell posts?

def get_orders(item):
    order_data = None
    r = None
    url = get_item_orders(item)
    #url = 'http://warframe.market/api/get_orders/Blueprint/Fluctus%20Stock'

    if not url:
        raise AssertionError("Invalid link")

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise RuntimeError('Error while connecting to ' + url)

    # Raise an exception in case of a bad response
    if not r.status_code == requests.codes.ok:
        raise RuntimeError('Bad response from ' + url)

    # Response.json() might raise ValueError
    try:
        order_data = r.json()
    except ValueError as e:
        raise RuntimeError('Bad JSON from ' + url) from e

    # Raise an exception in case of an empty response
    if not order_data:
        raise RuntimeError('Empty response from ' + url)


    online_sales = [Order(d) for d in order_data["response"]["sell"] if Order(d).online == True]

    return online_sales

def get_lowest_offer(item):
    online_orders = get_orders(item)

    lowest = min(online_orders, key=lambda o: o.price)
    return lowest

def get_average_offer(item):
    online_orders = get_orders(item)
    prices = [o.price for o in online_orders]

    avg_price = "{0:.1f}".format(float(sum(prices)) / max(len(prices), 1))
    num_offers = len(online_orders)
    return [avg_price, num_offers]


def setup(bot):
    bot.add_cog(Wfmarket(bot))
    reload_items()

reload_items()
