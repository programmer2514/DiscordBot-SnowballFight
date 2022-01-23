import discord
from discord.ext import commands
from discord.client import Client
import random
import json
import asyncio

description = '''A bot that allows users to have snowball fights in a Discord channel.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=['s!', 'S!'], description=description, intents=intents)
globalUserDict = {}
powerupNames = {'1a': 'Accuracy +10%',
                '1b': 'Accuracy +25%',
                '1c': 'Accuracy +50%',
                '2a': 'Shield 33%',
                '2b': 'Shield 66%',
                '2c': 'Shield 100%',
                '3a': 'Multiplier x2',
                '3b': 'Multiplier x3',
                '3c': 'Multiplier x4'}
try:
    with open('snowballs.json', 'r', encoding='utf-8') as f:
        globalUserDict = json.load(f)
    print('Config loaded successfully')
except:
    print('No config found! A new one will be created')

def sortingKey(x):
    try:
        val = int(x[1])
    except:
        val = 0
    return val

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(brief='Collects some snowballs.', description='''SYNTAX: s!collect
Collects a snowball and adds it to your pile.''')
async def collect(ctx):
    try:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = globalUserDict[str(ctx.author.id) + ".snowballs"] + 1
        print('Added 1 snowball to user {0} ({1})'.format(ctx.author.name, ctx.author.id))
    except:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = 1
        print('No previous snowball index found for user {0} ({1})! One will be created'.format(ctx.author.name, ctx.author.id))
    with open('snowballs.json', 'w', encoding='utf-8') as f:
        json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
    print('Settings file written successfully')
    await ctx.send('<@{0}> collected a snowball! They now have {1} snowball(s).'.format(ctx.author.id, globalUserDict[str(ctx.author.id) + ".snowballs"]))

@bot.command(brief='Throws a snowball at someone', description='''SYNTAX: s!throw [@]<username>
Throws a snowball at the specified user and gives you a coin if the throw is successful. Does not need the @ to work.''')
async def throw(ctx, member: discord.Member):
    try:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = globalUserDict[str(ctx.author.id) + ".snowballs"] - 1
        print('Removed 1 snowball from user {0} ({1})'.format(ctx.author.name, ctx.author.id))
    except:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = -1
        print('No previous snowball index found for user {0} ({1})! One will be created'.format(ctx.author.name, ctx.author.id))
    if (globalUserDict[str(ctx.author.id) + ".snowballs"] < 0):
        message = '''<@{0}> doesn't have any snowballs! Use `s!collect` to get some.'''.format(ctx.author.id)
        globalUserDict[str(ctx.author.id) + ".snowballs"] = 0
    else:
        try:
            randChance = 40 + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('1a') * 10) + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('1b') * 25) + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('1c') * 50) + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('4') * 15)
            print('Successfully applied throwing user modifiers')
        except:
            randChance = 40
            print('Throwing user does not have modifiers')
        try:
            randChance = randChance - (globalUserDict[str(member.id) + ".modifiers"].count('2a') * 33) - (globalUserDict[str(member.id) + ".modifiers"].count('2b') * 66) - (globalUserDict[str(member.id) + ".modifiers"].count('2c') * 100)
            print('Successfully applied targeted user modifiers')
        except:
            print('Targeted user does not have modifiers')
        if (random.randint(0, 99) < randChance):
            if (ctx.author.id == member.id):
                message = '''<@{0}> threw a snowball at themselves (for some reason)!
They now have {1} snowball(s) remaining.'''.format(ctx.author.id, globalUserDict[str(ctx.author.id) + ".snowballs"])
            else:
                try:
                    coins = pow(2,(globalUserDict[str(ctx.author.id) + ".modifiers"].count('3a') + globalUserDict[str(ctx.author.id) + ".modifiers"].count('5'))) * pow(3,globalUserDict[str(ctx.author.id) + ".modifiers"].count('3b')) * pow(4,globalUserDict[str(ctx.author.id) + ".modifiers"].count('3c'))
                    print('Successfully applied coin modifiers')
                except:
                    print('User does not have any coin modifiers')
                    coins = 1
                message = '''Splat! <@{0}> threw a snowball at <@{2}> and got \U0001FA99{3}!
They now have {1} snowball(s) remaining.'''.format(ctx.author.id, globalUserDict[str(ctx.author.id) + ".snowballs"], member.id, coins)
                try:
                    globalUserDict[str(ctx.author.id) + ".coins"] = globalUserDict[str(ctx.author.id) + ".coins"] + coins
                    print('Added {2} coin(s) to user {0} ({1})'.format(ctx.author.name, ctx.author.id, coins))
                except:
                    globalUserDict[str(ctx.author.id) + ".coins"] = coins
                    print('No previous coin index found for user {0} ({1})! One will be created'.format(ctx.author.name, ctx.author.id))
        else:
            message = '''<@{0}> threw a snowball, but it missed!
They now have {1} snowball(s) remaining.'''.format(ctx.author.id, globalUserDict[str(ctx.author.id) + ".snowballs"])
    with open('snowballs.json', 'w', encoding='utf-8') as f:
        json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
    print('Settings file written successfully')
    await ctx.send(message)

@bot.command(brief='Checks how many coins you have', description='''SYNTAX: s!coins
Shows you how many coins you currently have.''')
async def coins(ctx):
    try:
        await ctx.send("{0} currently has \U0001FA99{1}".format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".coins"]))
    except:
        await ctx.send("{0} currently has \U0001FA990. Hit some people with snowballs to get some".format(ctx.author.name))

@bot.command(brief='Opens the powerup/modifier shop', description='''SYNTAX: s!shop
Shows the index of the shop, where you can use s!buy to get powerups and modifiers in return for coins.''')
async def shop(ctx):
    try:
        coins = globalUserDict[str(ctx.author.id) + ".coins"]
    except:
        coins = 0
    await ctx.send('''```
Powerup Shop:
Welcome to the powerup shop! Use s!buy <itemID> to make your purchase
Example: s!buy 1b - Buys the Accuracy +25% powerup for \U0001FA9920
-----
{0} currently has \U0001FA99{1}
-----
Powerups (8 mins):
  1) *Accuracy   - Increases hit chance
     a) +10%       -  \U0001FA9910
     b) +25%       -  \U0001FA9920
     c) +50%       -  \U0001FA9935
  2) Shield      - Decreases chance of being hit
     a) 33%        -  \U0001FA9921
     b) 67%        -  \U0001FA9940
     c) 100%       -  \U0001FA9958
  3) *Multiplier - Increases coins recieved
     a) x2         -  \U0001FA9940
     b) x3         -  \U0001FA9955
     c) x4         -  \U0001FA9975
-----
Modifiers (permanent):
  4) *Base Accuracy +15%       -  \U0001FA99100
  5) *Permanent Multiplier x2  -  \U0001FA99200
-----
* = Stackable
```'''.format(ctx.author.name, coins))

@bot.command(brief='Buys a powerup/modifier', description='''SYNTAX: s!buy <num>[<subgroup>]
Buys the powerup or modifier specified by the 1-2 character store code (vending machine style).''')
async def buy(ctx, item: str):
    message = 'Incorrect item code entered!'
    try:
        coins = globalUserDict[str(ctx.author.id) + ".coins"]
    except:
        coins = 0
    try:
        modifiers = globalUserDict[str(ctx.author.id) + ".modifiers"]
    except:
        modifiers = ''
    if (len(item) == 1):
        if (item[0] == '4'):
            if (coins >= 100):
                globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '4'
                coins = coins - 100
                message = 'Modifier purchased successfully!'
                print('User {0} ({1}) bought modifier 4 for 100 coins'.format(ctx.author.name, ctx.author.id))
            else:
                message = 'Not enough coins!'
        if (item[0] == '5'):
            if (coins >= 200):
                globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '5'
                coins = coins - 200
                message = 'Modifier purchased successfully!'
                print('User {0} ({1}) bought modifier 5 for 200 coins'.format(ctx.author.name, ctx.author.id))
            else:
                message = 'Not enough coins!'
        globalUserDict[str(ctx.author.id) + ".coins"] = coins
        with open('snowballs.json', 'w', encoding='utf-8') as f:
            json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
        print('Settings file written successfully')
        await ctx.send(message + '''
{0} now has \U0001FA99{1}'''.format(ctx.author.name, coins))
    if (len(item) == 2):
        powerup = ''
        if (item[0] == '1'):
            if (item[1] == 'a'):
                if (coins >= 10):
                    globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '1a'
                    coins = coins - 10
                    powerup = '1a'
                    message = 'Powerup purchased successfully!'
                else:
                    message = 'Not enough coins!'
            if (item[1] == 'b'):
                if (coins >= 20):
                    globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '1b'
                    coins = coins - 20
                    powerup = '1b'
                    message = 'Powerup purchased successfully!'
                else:
                    message = 'Not enough coins!'
            if (item[1] == 'c'):
                if (coins >= 35):
                    globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '1c'
                    coins = coins - 35
                    powerup = '1c'
                    message = 'Powerup purchased successfully!'
                else:
                    message = 'Not enough coins!'
        if (item[0] == '2'):
            if (item[1] == 'a'):
                if (coins >= 21):
                    if '2a' not in modifiers:
                        globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '2a'
                        coins = coins - 21
                        powerup = '2a'
                        message = 'Powerup purchased successfully!'
                    else:
                        message = 'You already have that powerup!'
                else:
                    message = 'Not enough coins!'
            if (item[1] == 'b'):
                if (coins >= 40):
                    if '2b' not in modifiers:
                        globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '2b'
                        coins = coins - 40
                        powerup = '2b'
                        message = 'Powerup purchased successfully!'
                    else:
                        message = 'You already have that powerup!'
                else:
                    message = 'Not enough coins!'
            if (item[1] == 'c'):
                if (coins >= 58):
                    if '2c' not in modifiers:
                        globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '2c'
                        coins = coins - 58
                        powerup = '2c'
                        message = 'Powerup purchased successfully!'
                    else:
                        message = 'You already have that powerup!'
                else:
                    message = 'Not enough coins!'
        if (item[0] == '3'):
            if (item[1] == 'a'):
                if (coins >= 40):
                    globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '3a'
                    coins = coins - 40
                    powerup = '3a'
                    message = 'Powerup purchased successfully!'
                else:
                    message = 'Not enough coins!'
            if (item[1] == 'b'):
                if (coins >= 55):
                    globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '3b'
                    coins = coins - 55
                    powerup = '3b'
                    message = 'Powerup purchased successfully!'
                else:
                    message = 'Not enough coins!'
            if (item[1] == 'c'):
                if (coins >= 75):
                    globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + '3c'
                    coins = coins - 75
                    powerup = '3c'
                    message = 'Powerup purchased successfully!'
                else:
                    message = 'Not enough coins!'
        globalUserDict[str(ctx.author.id) + ".coins"] = coins
        with open('snowballs.json', 'w', encoding='utf-8') as f:
            json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
        print('Settings file written successfully')
        await ctx.send(message + '''
{0} now has \U0001FA99{1}'''.format(ctx.author.name, coins))
        if (len(powerup) > 0):
            print('User {0} ({1}) bought powerup {2} for 200 coins'.format(ctx.author.name, ctx.author.id, powerup))
            await asyncio.sleep(480)
            print('User {0} ({1}) powerup {2} expired'.format(ctx.author.name, ctx.author.id, powerup))
            globalUserDict[str(ctx.author.id) + ".modifiers"] = globalUserDict[str(ctx.author.id) + ".modifiers"].replace(powerup, '', 1)
            with open('snowballs.json', 'w', encoding='utf-8') as f:
                json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
            print('Settings file written successfully')
            await ctx.send("<@" + str(ctx.author.id) + "> Your powerup ({0}) has expired!".format(powerupNames[powerup]))

@bot.command(brief='Shows the global leaderboard', description='''SYNTAX: s!leaderboard
Shows the top ten users with the most coins. Spend wisely in the shop or your ranking may drop.''')
async def leaderboard(ctx):
    temp = sorted(globalUserDict.items(), key=sortingKey, reverse=True)
    leaderboard = []
    message = '''```
'''
    for i in temp:
        if '.coins' in i[0]:
            if (len(leaderboard) < 10):
                leaderboard.append(i)
            else:
                break
    if (len(leaderboard) > 0):
        print('Loaded leaderboard with {0} items'.format(len(leaderboard)))
        for i in range(len(leaderboard)):
            username = await bot.fetch_user(leaderboard[i][0][:-6])
            message = message + '''{2}: {0} - {1}
'''.format(username.name, "{0} coins".format(leaderboard[i][1]), i + 1)
    message = message + '```'
    await ctx.send(message)

bot.run('[REDACTED]')
