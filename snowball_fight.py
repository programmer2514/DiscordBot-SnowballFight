import discord
from discord.ext import commands
import random
import json
import asyncio


description = '''A bot that allows users to have snowball fights in a Discord channel.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=['s!', 'S!'], description=description, intents=intents)


globalUserDict = {}
powerupNames = {'1a': 'Accuracy +10%',
                '1b': 'Accuracy +25%',
                '1c': 'Accuracy +50%',
                '2a': 'Shield +20%',
                '2b': 'Shield +40%',
                '2c': 'Shield +60%',
                '3a': 'Multiplier x4',
                '3b': 'Multiplier x6',
                '3c': 'Multiplier x8',
                '4': 'Base Accuracy +5%',
                '5': 'Base Shield +5%',
                '6': 'Permanent Multiplier x2'}
powerupCosts = {'1a': 10,
                '1b': 20,
                '1c': 35,
                '2a': 20,
                '2b': 40,
                '2c': 60,
                '3a': 40,
                '3b': 60,
                '3c': 80,
                '4': 200,
                '5': 300,
                '6': 400}


try:
    with open('snowballs.json', 'r', encoding='utf-8') as f:
        globalUserDict = json.load(f)
    print('Config loaded successfully')
except:
    print('No config found! A new one will be created')


# Key for sorting leaderboard entries
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

    # Add a snowball
    try:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = globalUserDict[str(ctx.author.id) + ".snowballs"] + 1
        print('Added 1 snowball to user {0} ({1})'.format(ctx.author.name, ctx.author.id))
    except:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = 1
        print('No previous snowball index found for user {0} ({1})! One will be created'.format(ctx.author.name, ctx.author.id))

    # Write settings
    with open('snowballs.json', 'w', encoding='utf-8') as f:
        json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
    print('Settings file written successfully')

    # Send message
    await ctx.send('**{0}** collected a snowball! They now have {1} snowball(s).'.format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".snowballs"]))


@bot.command(brief='Throws a snowball at someone', description='''SYNTAX: s!throw [@]<username>
Throws a snowball at the specified user and gives you a coin if the throw is successful. Does not need the @ to work.''')
async def throw(ctx, member: discord.Member):

    # Remove a snowball
    try:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = globalUserDict[str(ctx.author.id) + ".snowballs"] - 1
        print('Removed 1 snowball from user {0} ({1})'.format(ctx.author.name, ctx.author.id))
    except:
        globalUserDict[str(ctx.author.id) + ".snowballs"] = -1
        print('No previous snowball index found for user {0} ({1})! One will be created'.format(ctx.author.name, ctx.author.id))

    # Throwing logic
    if (globalUserDict[str(ctx.author.id) + ".snowballs"] < 0):
        message = '''**{0}** doesn't have any snowballs! Use `s!collect` to get some.'''.format(ctx.author.name)
        globalUserDict[str(ctx.author.id) + ".snowballs"] = 0
    else:

        # Apply accuracy modifiers
        try:
            randChance = 40 + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('1a') * 10) + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('1b') * 25) + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('1c') * 50) + (globalUserDict[str(ctx.author.id) + ".modifiers"].count('4') * 5)
            if (randChance > 90):
                randChance = 90
                print('Throwing user has maxed out accuracy')
            print('Successfully applied throwing user modifiers')
        except:
            randChance = 40
            print('Throwing user does not have modifiers')

        # Apply shield modifiers
        try:
            randChance = randChance - (globalUserDict[str(member.id) + ".modifiers"].count('2a') * 20) - (globalUserDict[str(member.id) + ".modifiers"].count('2b') * 40) - (globalUserDict[str(member.id) + ".modifiers"].count('2c') * 60) - (globalUserDict[str(member.id) + ".modifiers"].count('5') * 5)
            if (randChance < 10):
                randChance = 10
                print('Targeted user has maxed out shield')
            print('Successfully applied targeted user modifiers')
        except:
            print('Targeted user does not have modifiers')

        # If user hits target
        if (random.randint(0, 99) < randChance):

            # If the user targets themselves or a bot
            if (ctx.author.id == member.id):
                message = '''**{0}** threw a snowball at themselves (for some reason)!
They now have {1} snowball(s) remaining.'''.format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".snowballs"])
            elif (member.bot):
                message = '''**{0}**'s snowball was deflected by **{2}**'s magical bot powers!
They now have {1} snowball(s) remaining.'''.format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".snowballs"], member.name)

            else:
                # Apply coin modifiers
                try:
                    coins = (globalUserDict[str(ctx.author.id) + ".modifiers"].count('3a') * 4) * (globalUserDict[str(ctx.author.id) + ".modifiers"].count('3b') * 6) * (globalUserDict[str(ctx.author.id) + ".modifiers"].count('3c') * 8) * (globalUserDict[str(ctx.author.id) + ".modifiers"].count('6') * 2)
                    if (coins < 1):
                        coins = 1
                        print('User does not have any coin modifiers')
                    else:
                        print('Successfully applied coin modifiers')
                except:
                    print('User does not have any coin modifiers')
                    coins = 1

                message = '''Splat! **{0}** threw a snowball at **{2}** and got \U0001FA99{3}!
They now have {1} snowball(s) remaining.'''.format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".snowballs"], member.name, coins)

                # Add coins to user
                try:
                    globalUserDict[str(ctx.author.id) + ".coins"] = globalUserDict[str(ctx.author.id) + ".coins"] + coins
                    print('Added {2} coin(s) to user {0} ({1})'.format(ctx.author.name, ctx.author.id, coins))
                except:
                    globalUserDict[str(ctx.author.id) + ".coins"] = coins
                    print('No previous coin index found for user {0} ({1})! One will be created'.format(ctx.author.name, ctx.author.id))

        # If user misses target
        else:
            message = '''**{0}** threw a snowball, but it missed!
They now have {1} snowball(s) remaining.'''.format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".snowballs"])

    # Write settings
    with open('snowballs.json', 'w', encoding='utf-8') as f:
        json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
    print('Settings file written successfully')

    # Send message
    await ctx.send(message)


@bot.command(brief='Checks how many coins you have', description='''SYNTAX: s!coins
Shows you how many coins you currently have.''')
async def coins(ctx):
    try:
        await ctx.send("**{0}** currently has \U0001FA99{1}".format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".coins"]))
    except:
        await ctx.send("**{0}** currently has \U0001FA990. Hit some people with snowballs to get some".format(ctx.author.name))


@bot.command(brief='Opens the powerup/modifier shop', description='''SYNTAX: s!shop
Shows the index of the shop, where you can use s!buy to get powerups and modifiers in return for coins.''')
async def shop(ctx):

    # Get coins
    try:
        coins = globalUserDict[str(ctx.author.id) + ".coins"]
    except:
        coins = 0

    # Send message
    await ctx.send('''```
Powerup Shop:
Welcome to the powerup shop! Use s!buy <itemID> to make your purchase
Example: s!buy 1b - Buys the Accuracy +25% powerup for \U0001FA99{3}
-----
**{0}** currently has \U0001FA99{1}
-----
Powerups (8 mins):
  1) Accuracy   - Increases hit chance
     a) +10%       -  \U0001FA99{2}
     b) +25%       -  \U0001FA99{3}
     c) +50%       -  \U0001FA99{4}
  2) Shield      - Decreases chance of being hit
     a) 20%        -  \U0001FA99{5}
     b) 40%        -  \U0001FA99{6}
     c) 60%       -  \U0001FA99{7}
  3) Multiplier - Increases coins recieved
     a) x4         -  \U0001FA99{8}
     b) x6         -  \U0001FA99{9}
     c) x8         -  \U0001FA99{10}
-----
Modifiers (permanent):
  4) *Base Accuracy +5%       -  \U0001FA99{11}
  5) *Base Shield +5%       -  \U0001FA99{12}
  6) *Permanent Multiplier x2  -  \U0001FA99{13}
-----
NOTES:
  Powerups are stackable.
  Shield/accuracy are capped between 10% and 90%
  Prices will scale as you accumulate powerups
```'''.format(ctx.author.name, coins, powerupCosts['1a'] * (coins//1000 + (not coins//1000)), powerupCosts['1b'] * (coins//1000 + (not coins//1000)), powerupCosts['1c'] * (coins//1000 + (not coins//1000)), powerupCosts['2a'] * (coins//1000 + (not coins//1000)), powerupCosts['2b'] * (coins//1000 + (not coins//1000)), powerupCosts['2c'] * (coins//1000 + (not coins//1000)), powerupCosts['3a'] * (coins//1000 + (not coins//1000)), powerupCosts['3b'] * (coins//1000 + (not coins//1000)), powerupCosts['3c'] * (coins//1000 + (not coins//1000)), powerupCosts['4'] * (coins//1000 + (not coins//1000)), powerupCosts['5'] * (coins//1000 + (not coins//1000)), powerupCosts['6'] * (coins//1000 + (not coins//1000))))


@bot.command(brief='Buys a powerup/modifier', description='''SYNTAX: s!buy <num>[<subgroup>]
Buys the powerup or modifier specified by the 1-2 character store code (vending machine style).''')
async def buy(ctx, item: str):

    message = 'Incorrect item code entered!'

    # Get coins
    try:
        coins = globalUserDict[str(ctx.author.id) + ".coins"]
    except:
        globalUserDict[str(ctx.author.id) + ".coins"] = 0
        coins = 0

    # Get modifiers
    try:
        modifiers = globalUserDict[str(ctx.author.id) + ".modifiers"]
    except:
        globalUserDict[str(ctx.author.id) + ".modifiers"] = ''
        modifiers = ''

    # Buy item
    if (item in powerupNames.keys()):
        if (coins >= powerupCosts[item] * (coins//1000 + (not coins//1000))):
            globalUserDict[str(ctx.author.id) + ".modifiers"] = modifiers + item
            globalUserDict[str(ctx.author.id) + ".coins"] = coins - (powerupCosts[item] * (coins//1000 + (not coins//1000)))
            if (len(item) == 1):
                message = 'Modifier purchased successfully!'
                print('User {0} ({1}) bought modifier {2} for {3} coins'.format(ctx.author.name, ctx.author.id, item, powerupCosts[item] * (coins//1000 + (not coins//1000))))
            else:
                message = 'Powerup purchased successfully!'
                print('User {0} ({1}) bought powerup {2} for {3} coins'.format(ctx.author.name, ctx.author.id, item, powerupCosts[item] * (coins//1000 + (not coins//1000))))
        else:
            message = 'Not enough coins!'
    else:
        message = 'Incorrect item code entered!'

    # Write settings
    with open('snowballs.json', 'w', encoding='utf-8') as f:
        json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
    print('Settings file written successfully')

    # Send message
    await ctx.send(message + '''
**{0}** now has \U0001FA99{1}'''.format(ctx.author.name, globalUserDict[str(ctx.author.id) + ".coins"]))

    # If item is a powerup, expire it
    if (len(item) == 2):
        await asyncio.sleep(480)
        print('User {0} ({1}) powerup {2} expired'.format(ctx.author.name, ctx.author.id, item))
        globalUserDict[str(ctx.author.id) + ".modifiers"] = globalUserDict[str(ctx.author.id) + ".modifiers"].replace(item, '', 1)

        # Write settings
        with open('snowballs.json', 'w', encoding='utf-8') as f:
            json.dump(globalUserDict, f, ensure_ascii=False, indent=4)
        print('Settings file written successfully')

        # Send message
        await ctx.send("<@{0}> Your powerup (**{1}**) has expired!".format(ctx.author.id, powerupNames[item]))


@bot.command(brief='Shows the global leaderboard', description='''SYNTAX: s!leaderboard
Shows the top ten users with the most coins. Spend wisely in the shop or your ranking may drop.''')
async def leaderboard(ctx):

    temp = sorted(globalUserDict.items(), key=sortingKey, reverse=True)
    leaderboard = []
    message = '''```
'''

    # Get top 10 scores
    for i in temp:
        if '.coins' in i[0]:
            if (len(leaderboard) < 10):
                leaderboard.append(i)
            else:
                break
    del temp

    # Format scores and append to message
    if (len(leaderboard) > 0):
        print('Loaded leaderboard with {0} items'.format(len(leaderboard)))
        for i in range(len(leaderboard)):
            username = await bot.fetch_user(leaderboard[i][0][:-6])
            message = message + '''{0}: {1} - {2} coins
'''.format(i + 1, username.name, leaderboard[i][1])
    message = message + '```'

    # Send message
    await ctx.send(message)


bot.run('[REDACTED]')
