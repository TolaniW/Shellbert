import discord, json
from discord.activity import Game
from discord.ext import commands, tasks
import requests
import twitter, asyncio

api = twitter.Api()
with open('config.json') as f:
        f = json.load(f)
        
api = twitter.Api(
    consumer_key=f['client_id'],
    consumer_secret=f['client_secret'],
    access_token_key=f['api_token'],
    access_token_secret=f['api_secret'],
    tweet_mode='extended'
)
api.VerifyCredentials()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents)
client.tried = False
# client.remove_command("help")

@client.event
async def on_ready():
    import os
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f"cogs.{filename[:-3]}")
    await client.change_presence(activity=Game(name=".help"))
    with open("config.json") as file:
        f = json.load(file)

    client.welcome = client.guilds[0].get_channel(f['welcome_channel'])
    client.twitter = client.guilds[0].get_channel(f['twitter_channel'])
    client.twitch = client.guilds[0].get_channel(f['twitch_channel'])
    loop.start()
    print("READY!")

def is_live(userName):
    with open('config.json') as f:
        f = json.load(f)
    url = 'https://api.twitch.tv/helix/streams?user_login='+userName
    API_HEADERS = {
    'Client-ID' : f["client_id"],
    'Authorization' : 'Bearer '+f['twitch_access_token'],
    }

    try:
        req = requests.get(url, headers=API_HEADERS)
        jsondata = req.json()
        if len(jsondata['data']) == 1:
            client.tried = False
            return True
        else:
            client.tried = False
            return False
    except Exception as e:
        if client.tried:
            client.tried = False
            raise e
        else:
            client.tried = True
            body = {
                'client_id': f["client_id"],
                'client_secret': f["client_secret"],
                "grant_type": 'client_credentials'
            }
            r = requests.post('https://id.twitch.tv/oauth2/token', body).json()
            f['twitch_access_token'] = r['access_token']
            with open('config.json', 'w') as file:
                json.dump(f, file, indent=2, separators=(',', ': '))
            is_live(userName)

@tasks.loop(seconds=12)
async def loop():
    # TWITCH LIVE CHECK!
    with open('config.json') as f:
        f = json.load(f)

    for streamer in f['streamers']:
        if is_live(streamer):
            try:
                if f['informed'][streamer] != "yes":
                    await client.twitch.send(f"{streamer} is currently live! Go check out their stream at: https://www.twitch.tv/{streamer}")
                    f['informed'][streamer] = "yes"
            except KeyError:
                f['informed'][streamer] = "yes"
                await client.twitch.send(f"{streamer} is currently live! Go check out their stream at: https://www.twitch.tv/{streamer}")
        else:
            f['informed'][streamer] = "no"

        await asyncio.sleep(0.5)

    # TWITTER NEW TWEET CHECK!
    for user in f['twitter_users']:
        tweet = api.GetUserTimeline(screen_name=user, count=1, exclude_replies=True, trim_user=True, include_rts=False)[0]
        try: 
            if f['latest'][user] != tweet.id:
                f['latest'][user] = tweet.id
                await client.twitter.send(embed=discord.Embed(title=f"{tweet.user.name} has tweeted a new tweet", description=tweet.full_text, color=discord.Color.green()))
        except: f['latest'][user] = tweet.id

    with open('config.json', 'w') as file:
            json.dump(f, file, indent=2, separators=(',', ': '))

@client.event
async def on_member_join(member):
    await client.welcome.send(f"""Hi {member.mention}! Welcome to the Hut! There’s plenty do, spells to master, potions to brew, and so much more, but most importantly have fun! And please feel free to introduce yourself in the introduction channel!""")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("The command you specified was not found. Type .help to see all available commands.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing a required argument.")

    elif isinstance(error, discord.ext.commands.errors.MissingPermissions) or isinstance(error, discord.Forbidden) or isinstance(error, discord.ext.commands.errors.MissingAnyRole):
        await ctx.send("Sorry. You don't have the permission for that command.")

    else: await ctx.send(error)

client.run(open('token.txt', 'r').read().strip())
