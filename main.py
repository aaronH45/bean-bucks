import os
import discord
from discord.ext import commands
import json

# from flask import Flask # Import Flask Class
# app = Flask(__name__) # Create an Instance
# @app.route('/') # Route the Function
# def main(): # Run the function
# 	return 'Hello World'

bot = commands.Bot(command_prefix='$')
token = os.environ['token']

try:
    with open("users.json") as fp:
        users = json.load(fp)
except Exception:
    users = {}

active_bets = {}
bet_confirmer = {}


@bot.event
async def on_ready():
    print('Loaded leader')
    print(users)
    print()
    print('We have logged in as {0.user}'.format(bot))


def save_users():
    with open("users.json", "w+") as fp:
        json.dump(users, fp, indent=4)


@bot.command()
async def bean(ctx):
    await ctx.send('Bean Fat')


def add_bb(user: discord.User, amount: int):
    id = str(user.id)
    if id not in users.keys():
        users[id] = {}
        users[id]['name'] = user.name
    new_balance = users[id].get("bb", 0) + amount
    users[id]["bb"] = new_balance
    save_users()
    return new_balance


# @bot.command()
# async def add(ctx, user: discord.User, bean_bucks: int):
#     new_balance = add_bb(user, bean_bucks)
#     await ctx.send("{} now has {} Bean bucks".format(user.name, new_balance))


@bot.command()
async def ledger(ctx):
    msg = '**Bean Bucks Betting Bodega Balance **\n'
    sorted_users = (sorted(users.items(),
                           key=lambda item: item[1]['bb'],
                           reverse=True))
    for id, info in sorted_users:
        msg = msg + '\t \t **{}**: {} Bean Bucks'.format(
            info['name'], info["bb"]) + '\n'
    await ctx.send(msg)


bot.remove_command('help')


@bot.command()
async def help(ctx):
    msg = '''**Bean Bucks Bots Bodacious Behavior**
         **$ledger**: Check Balances
         **$bet @person amount**: To place a bet
         **$bean**: secret message'''
    await ctx.send(msg)


@bot.command()
async def bet(ctx, user2: discord.User, amount: int):
    if amount <= 5000:
        user1 = ctx.message.author
        msg = await ctx.send('{} bet {} {} BeanBucks'.format(
            user1.name, user2.name, amount))
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')
        active_bets[msg] = (user1, user2, amount)
        bet_confirmer[msg] = [0, 0]
    else:
        await ctx.send("Betting limit of 5k exceed. Broke Bitches.")


def settle_bet(winner: discord.User, loser: discord.User, amount: int):
    add_bb(winner, amount)
    add_bb(loser, -1 * amount)
    return '{} won {} BeanBucks from {}'.format(winner.name, amount,
                                                loser.name)


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message in active_bets and user.id != bot.user.id:
        user1, user2, amount = active_bets[reaction.message]

        if user.id == user1.id:
            if str(reaction) == '👍':
                bet_confirmer[reaction.message][0] = 1
            elif str(reaction) == '👎':
                bet_confirmer[reaction.message][0] = -1
        elif user.id == user2.id:
            if str(reaction) == '👍':
                bet_confirmer[reaction.message][1] = 1
            elif str(reaction) == '👎':
                bet_confirmer[reaction.message][1] = -1

        total = sum(bet_confirmer[reaction.message])

        if abs(total) == 2:
            user1, user2, amount = active_bets.pop(reaction.message)
            if total == 2:
                msg = settle_bet(user1, user2, amount)
                await reaction.message.channel.send(msg)
            elif total == -2:
                msg = settle_bet(user2, user1, amount)
                await reaction.message.channel.send(msg)


# @bot.event
# async def on_reaction_add(reaction, user):
#     if reaction.message in active_bets and user.id != bot.user.id:
#         user1,user2, amount = active_bets.pop(reaction.message)
#         if str(reaction) == '👍':
#             msg = settle_bet(user1, user2, amount)
#             await reaction.message.channel.send(msg)
#         elif str(reaction) == '👎':
#             msg = settle_bet(user2, user1, amount)
#             await reaction.message.channel.send(msg)

bot.run(token)

# app.run(host='0.0.0.0', port=5000, debug=True) # Run the Application (in debug mode)
