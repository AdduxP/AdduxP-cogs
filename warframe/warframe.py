import discord
from discord.ext import commands
from datetime import datetime
import requests

class Warframe:
    """A bunch of Warframe-related cogs!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wfnews")
    async def news(self):
        """Get the latest in Warframe news!"""
        await self.bot.say(get_condensed_news_string())

    @commands.command(name="wfinvasion")
    async def invasion(self):
        """Who's trying to conquer who this time?"""
        await self.bot.say(get_invasion_string())
    
    @commands.command(name="wffissures")
    async def fissures(self):
        """Fetch void fissure missions!"""
        await self.bot.say(get_fissure_string())
        
    @commands.command(name="wfdeals")
    async def deals(self):
        """Check out Darvo's daily deal!"""
        deals = get_deal_string().__str__()
        await self.bot.say("Here's what Darvo's got today:\n" + deals)
        
def setup(bot):
    bot.add_cog(Warframe(bot))

#### Helper Functions for NEWS ####

class Newsline:
    """This class represents a news item and is initialized with
    data in text format
    """

    def __init__(self, data):
        info = data.split('|')
        self.id         = info[0]
        self.link       = info[1]
        self.time       = datetime.fromtimestamp(int(info[2]))
        self.text       = info[3]

    def __str__(self):
        """Returns a string with the description of the news item
        """

        return '[{} ago]: **{}**: *<{}>*'.format(self.get_elapsed_time(),
                                              self.text, self.link)

    def get_elapsed_time(self):
        """Returns a string containing the time that has passed since
        the news item was published
        """

        return self.timedelta_to_string(datetime.now() - self.time)

    def timedelta_to_string(self, td):
        """Returns a custom string representation of a timedelta object
        Parameters
        ----------
        td : timedelta
            timedelta object to be represented as a string
        """
    
        seconds = int(td.total_seconds())
        time_string = ''
    
        if seconds >= 86400:        # Seconds in a day
            time_string = "{0}d"
        elif seconds >= 3600:
            time_string = "{1}h {2}m"
        else:
            time_string = "{2}m"
    
        return time_string.format(seconds // 86400, seconds // 3600, (seconds % 3600) // 60)


def get_news():
    url = 'https://deathsnacks.com/wf/data/news_raw.txt'
    news_data = None
    r = None
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise RuntimeError('Error while connecting to ' + url)

    # Raise an exception in case of a bad response
    if not r.status_code == requests.codes.ok:
        raise RuntimeError('Bad response from ' + url)

    news_data = r.text.split('\n')
    news_data.pop()

    # Raise an exception in case of an empty response
    if not news_data:
        raise RuntimeError('Empty response from ' + url)

    return [Newsline(n) for n in news_data]


def get_news_string():
    """Returns a string with the news"""

    news_string = ""
    for n in get_news():
        news_string += str(n) + '\n\n'

    return news_string

def get_condensed_news_string():
    """Return a string with only the most current 3 entries"""
    news_string = ""
    newslines = get_news()
    if (len(newslines) < 3):
        for n in get_news():
            news_string += str(n) + '\n\n'
    else: 
        for i in range(0, 3):
            news_string += str(newslines[i]) + '\n\n'
    return news_string
    
#### Helper Functions for INVASION ####

class Invasion:
    """This class represents an invasion, and is initialized with
    data in JSON format
    """

    def __init__(self, data):
        self.id         = data['Id']
        self.node       = data['Node']
        self.planet     = data['Region']
        self.faction1   = data['InvaderInfo']['Faction']
        self.type1      = data['InvaderInfo']['MissionType']
        self.reward1    = data['InvaderInfo']['Reward']
        self.level1_min = data['InvaderInfo']['MinLevel']
        self.level1_max = data['InvaderInfo']['MaxLevel']
        self.faction2   = data['DefenderInfo']['Faction']
        self.type2      = data['DefenderInfo']['MissionType']
        self.reward2    = data['DefenderInfo']['Reward']
        self.level2_min = data['DefenderInfo']['MinLevel']
        self.level2_max = data['DefenderInfo']['MaxLevel']
        self.completion = data['Percentage']
        self.ETA        = data['Eta']
        self.desc       = data['Description']

    def __str__(self):
        """Returns a string with all the information about
        this invasion
        """
        if self.faction1 == 'Infestation':
            invasionString = ('**{0} ({1})** \n'
                              '{2} ({8})\n'
                              '*{9:.2f}% - {10}*')
        else:
            invasionString = ('**{0} ({1}) - {2}**\n'
                              '{3} ({5}) vs. \n'
                              '{6} ({8})\n'
                              '*{9:.2f}% - {10}*')
        return invasionString.format(self.node, self.planet, self.desc,
                                     self.faction1, self.type1,
                                     self.reward1, self.faction2,
                                     self.type2, self.reward2,
                                     self.completion, self.ETA)

    def get_rewards(self):
        """Returns a list containing the invasion's rewards excluding credits
        """
        return [i for i in [self.reward1, self.reward2] if 'cr' not in i]

def get_invasions():
    """ Returns a list of Invasion objects containing all active
    invasions
    Throws RuntimeError in case of a bad response
    """
    invasion_data = None
    r = None
    url = 'https://deathsnacks.com/wf/data/invasion.json'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise RuntimeError('Error while connecting to ' + url)

    # Raise an exception in case of a bad response
    if not r.status_code == requests.codes.ok:
        raise RuntimeError('Bad response from ' + url)

    # Response.json() might raise ValueError
    try:
        invasion_data = r.json()
    except ValueError as e:
        raise RuntimeError('Bad JSON from ' + url) from e

    # Raise an exception in case of an empty response
    if not invasion_data:
        raise RuntimeError('Empty response from ' + url)

    return [Invasion(d) for d in invasion_data]

def get_invasion_string():
    """ Returns a string with all current invasions"""

    invasion_string = ''
    invasions = get_invasions()

    for i in invasions:
        invasion_string += str(i) + '\n\n'

    return invasion_string
    
    
#### Helper Functions for FISSURES ####

class Fissure:
    """This class represents an fissure, and is initialized with
    data in JSON format
    """

    def __init__(self, data):
        self.region     = data['Region']
        self.seed       = data['Seed']
        self.node       = data['Node']
        self.modifier   = data['Modifier'][-2:]
        self.endtime    =  datetime.fromtimestamp(int(data['Expiry']['sec']))

    def __str__(self):
        """Returns a string with all the information about
        this fissure
        """
        return '{} | **{}**  [{} left]'.format(self.modifier, self.node, self.get_eta())
        
    def get_eta(self):
        """Returns a string containing the time that has passed since
        the news item was published
        """
        return self.timedelta_to_string(self.endtime - datetime.now())

    def timedelta_to_string(self, td):
        """Returns a custom string representation of a timedelta object
        Parameters
        ----------
        td : timedelta
            timedelta object to be represented as a string
        """

        seconds = int(td.total_seconds())
        time_string = ''

        if seconds >= 86400:        # Seconds in a day
            time_string = "{0}d"
        elif seconds >= 3600:
            time_string = "{1}h {2}m"
        else:
            time_string = "{2}m"

        return time_string.format(seconds // 86400, seconds // 3600, (seconds % 3600) // 60)


def get_fissure():
    """ Returns a list of Fissure objects containing all active
    void fissures
    Throws RuntimeError in case of a bad response
    """
    fissure_data = None
    r = None
    url = 'https://deathsnacks.com/wf/data/activemissions.json'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise RuntimeError('Error while connecting to ' + url)

    # Raise an exception in case of a bad response
    if not r.status_code == requests.codes.ok:
        raise RuntimeError('Bad response from ' + url)

    # Response.json() might raise ValueError
    try:
        fissure_data = r.json()
    except ValueError as e:
        raise RuntimeError('Bad JSON from ' + url) from e

    # Raise an exception in case of an empty response
    if not fissure_data:
        raise RuntimeError('Empty response from ' + url)

    return [Fissure(d) for d in fissure_data]

def get_fissure_string():
    """ Returns a string with all current fissures"""

    fissure_data = ''
    fissures = get_fissure()

    for f in fissures:
        fissure_data += str(f) + '\n'

    return fissure_data
    
    
#### Helper Functions for DEALS ####

class Deal:
    """This class represents an fissure, and is initialized with
    data in JSON format
    """

    def __init__(self, data):
        self.item       = data['StoreItem']
        self.discount   = data['Discount']
        self.original   = data['OriginalPrice']
        self.saleprice  = data['SalePrice']
        self.amttotal   = data['AmountTotal']
        self.amtsold    = data['AmountSold']
        self.endtime    = datetime.fromtimestamp(int(data['Expiry']['sec']))

        self.eta        = self.timedelta_to_string(self.endtime
                                                    - datetime.now())
        self.amtleft    = int(self.amttotal) - int(self.amtsold)


    def __str__(self):
        """Returns a string with all the information about
        this fissure
        """
        return '**{}**: {}p ({}%  off) | {}/{} left'.format(self.item, self.saleprice,
                                                        self.discount, self.amtleft,
                                                        self.amttotal)


    def timedelta_to_string(self, td):
        """Returns a custom string representation of a timedelta object
        Parameters
        ----------
        td : timedelta
            timedelta object to be represented as a string
        """

        seconds = int(td.total_seconds())
        time_string = ''

        if seconds >= 86400:        # Seconds in a day
            time_string = "{0}d"
        elif seconds >= 3600:
            time_string = "{1}h {2}m"
        else:
            time_string = "{2}m"

        return time_string.format(seconds // 86400, seconds // 3600, (seconds % 3600) // 60)


def get_deal_string():
    """ Returns a string with all current fissures"""
    deal_data = None
    r = None
    url = 'https://deathsnacks.com/wf/data/daily_deals.json'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise RuntimeError('Error while connecting to ' + url)

    # Raise an exception in case of a bad response
    if not r.status_code == requests.codes.ok:
        raise RuntimeError('Bad response from ' + url)

    # Response.json() might raise ValueError
    try:
        deal_data = r.json()
    except ValueError as e:
        raise RuntimeError('Bad JSON from ' + url) from e

    # Raise an exception in case of an empty response
    if not deal_data:
        raise RuntimeError('Empty response from ' + url)

    return [Deal(d) for d in deal_data][0]