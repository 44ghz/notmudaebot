# bot.py
import os
import random
import discord
import time

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')
CHANNEL = os.getenv('CHANNEL')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$$', intents = intents)
members = []
text_channel: discord.TextChannel

#### Values for marriage messages

marriage_message = "are now married"
marriage_message_separator = " and "
emoji_for_marriage = ":sparkling_heart:"
emoji_length_for_marriage = len(emoji_for_marriage) + 1 # Add 1 for space after emoji

####

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if int(guild.id) == int(GUILD):
            global members
            members = list(m.name for m in filter(lambda member: member.bot == False, guild.members))
        for channel in guild.text_channels:
            if int(channel.id) == int(CHANNEL):
                global text_channel
                text_channel = channel

    print("NotMudae is connected to Discord!")

@bot.command(name='cl', help="The shortened version of the $$claims command", case_insensitive=True)
async def get_claims_short(ctx):
    await get_claims(ctx)

# Construct response from claims messages
@bot.command(name='claims', help="See who has claims left on this rotation", case_insensitive=True)
async def get_claims(ctx):
    global text_channel
    now = datetime.utcnow()

    # In UTC, the claim intervals are every 3 hours and the hours at which claims reset are a multiple of 3 (6:23 AM UTC, 9:23 AM UTC, etc)
    # Finding the modulo of that will give us the amount of hours that have passed since the previous rotation
    difference = now.time().hour % 3

    # if the difference is 0 but the minutes are less than 23, use the previous interval (subtract 3)
    if difference == 0 and now.minute < 23:
        difference = 3

    interval_difference = datetime.utcnow() + timedelta(hours = difference * -1)
    window = datetime(interval_difference.year, interval_difference.month, interval_difference.day, interval_difference.hour, 23)

    messages = await text_channel.history(limit = 10000, after = window, oldest_first = True).flatten()

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
