# chromadrive-cogs
Some sample cogs (plugins) for Cephalon Touen, the bot. They do various small things - like lookups and reminders. There's also a few Warframe-related cogs if that's your kind of thing.

To be used with the in-bot downloader by adding it with:  
`!cog repo add chromadrive-cogs https://github.com/chromadrive/chromadrive-cogs`
`!cog activate chromadrive-cogs`


### chat

- `!chat [text]` or `@[Mention] [text]` to chat with the bot.
- `!chat toggle` to turn @mention replying on/off

### quote
- `!bash [num]` retrieves the specified number of quotes from bash.org. Default 1, max 5.
- `!quotes [query] [num]` retrieves the specified number of quotes from a specified author. Max 5.

### remindme

- `!remindme [quantity] [time_unit] [text]` sends you `<text>` when the time is up.

### strawpoll

- `!strawpoll [question] [options]` to create a strawpoll. Example usage: `strawpoll What's your favorite dessert?; Cake; Ice Cream; Pastries`
  - Can use `!captcha` and `!multi` after setting a strawpoll to toggle captcha and multiple voting, respectively

### warframe

- `!news` gets the latest Warframe news
- `!invasion` reports all current in-game invasion events
- `!fissures` reports all active in-game fissures
- `!deals` reports all active in-game market deals
- `!earth` reports current day/night cycle status on Earth

### wf-market

- `!pricecheck [item]` looks up `[item]`'s current trades on Warframe Market and reports back the five lowest available ones.
- `!getsellers [item]` gives a list of sellers with an active trade for `[item]`