# bot.py
import os
import random
import discord
import time
import threading

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands

# Environment variables
load_dotenv('.env')
TOKEN = os.environ['DISCORD_TOKEN']
GUILD = os.environ['GUILD']
CHANNEL = os.environ['CHANNEL']
FILTER_INACTIVE = bool(os.environ['FILTER_INACTIVE'])

client = discord.Client()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$$', intents = intents)

#### Global values

confirmation_emoji = "👍"
marriage_message = "are now married"
members = []
inactive_users = ["danox574", "Supedo no Esu", "JayRoss13" ]
text_channel: discord.TextChannel

####

@bot.event
async def on_ready():
    global FILTER_INACTIVE

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="it's called anime dad"))
    for guild in bot.guilds:
        if int(guild.id) == int(GUILD):
            global members
            members = list(m.name for m in filter(lambda member: member.bot == False, guild.members))
        for channel in guild.text_channels:
            if int(channel.id) == int(CHANNEL):
                global text_channel
                text_channel = channel 

    print("NotMudae is connected to Discord!")

@bot.command(name="ti", help="Shortened version of the " + str(bot.command_prefix) + "inactive command")
async def ti(ctx):
    await toggle_inactive_users(ctx)

@bot.command(name='inactive', help="Filter out users from claims and rolls information that haven't sent a message in the past 24 hours", case_insensitive=True)
async def toggle_inactive_users(ctx):
    global FILTER_INACTIVE

    FILTER_INACTIVE = not FILTER_INACTIVE

    inclusion = "included"

    if (FILTER_INACTIVE):
        inclusion = "excluded"

    os.environ["FILTER_INACTIVE"] = str(FILTER_INACTIVE)

    await ctx.send("Inactive users " + inclusion)

@bot.command(name='cl', help="The shortened version of the " + str(bot.command_prefix) + "claims command", case_insensitive=True)
async def get_claims_short(ctx):
    await get_claims(ctx)

# Construct response from claims messages
@bot.command(name='claims', help="See who has claims left on this rotation", case_insensitive=True)
async def get_claims(ctx):
    global text_channel
    global FILTER_INACTIVE

    async with text_channel.typing():
        now = datetime.utcnow()

        # In UTC, the claim intervals are every 3 hours and the hours at which claims reset are a multiple of 3 (6:23 AM UTC, 9:23 AM UTC, etc)
        # Finding the modulo of that will give us the amount of hours that have passed since the previous rotation
        difference = now.time().hour % 3

        # if the difference is 0 but the minutes are less than 23, use the previous interval (subtract 3)
        if difference == 0 and now.minute < 23:
            difference = 3

        interval_difference = datetime.utcnow() + timedelta(hours = difference * -1)
        window = datetime(interval_difference.year, interval_difference.month, interval_difference.day, interval_difference.hour, 23)

        messages = await text_channel.history(limit = 3000, after = window, oldest_first = True).flatten()

        bot_messages = list(filter(lambda m: m.author.bot == True, messages))
        #messages_content = list(([m.content, m.created_at] for m in bot_messages)) uncomment for multiple attributes if needed
        messages_content = list(m.content for m in bot_messages)
    
        members_married = []
        members_with_claims = []

        for message in messages_content:
            if marriage_message in message:
                left = get_index(message, "**", 1) + 2 # Add two for bold markdown
                right = get_index(message, "**", 2)
                member = message[left:right]
                members_married.append(member.strip())

        # Find anyone not in the list
        members_with_claims = list(set(members) - set(members_married))

        if (FILTER_INACTIVE):
            members_with_claims = list(set(members_with_claims) - set(inactive_users))

        members_with_claims = sorted(members_with_claims, key = str.casefold)

        s = "\n"

        embed = discord.Embed(color=0x875d5d)
        embed.title = "People with claims" 
        embed.description = s.join(members_with_claims)

        if len(members_with_claims) > 0:
            await ctx.send(embed=embed)
        else:
            await ctx.send("Everyone's claimed for this interval!")


def get_index(input_string, sub_string, ordinal):
    current = -1
    for i in range(ordinal):
        current = input_string.index(sub_string, current + 1)

    return current

bot.run(TOKEN)
