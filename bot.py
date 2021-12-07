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
intents.messages = True
intents.members = True
bot = commands.Bot(command_prefix='$$', intents = intents)


#### Global values

marriage_messages = ["are now married", "into the *Fine Arts Exhibit*"]
members = []
members_married = []
inactive_users = ["burntLinoleum", "danox574", "Supedo no Esu", "JayRoss13" ]
text_channel: discord.TextChannel
interval_reset_minute = 23
new_interval = False
now = datetime.utcnow()
reset_intervals = [
    1,
    4,
    7,
    10,
    13,
    16,
    19,
    22
    ]
interval_tracker = 1

####


@bot.event
async def on_ready():
    global FILTER_INACTIVE
    global now

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="it's called anime dad"))
    for guild in bot.guilds:
        if int(guild.id) == int(GUILD):
            global members
            members = list(m.name for m in filter(lambda member: member.bot == False, guild.members))
        for channel in guild.text_channels:
            if int(channel.id) == int(CHANNEL):
                global text_channel
                text_channel = channel 

    print("Getting historical claims")

    now = datetime.utcnow()
    await set_historical_claims()
    print(*get_claims())

    print("NotMudae is connected to Discord!")


@bot.event
async def on_message(ctx):
    global members_with_claims
    global members_married
    global marriage_messages
    global new_interval
    global now
    global interval_tracker

    now = datetime.utcnow()
    new_interval = False

    if int(ctx.channel.id) != int(CHANNEL):
        return

    if now.hour > interval_tracker or (interval_tracker == 24 and now.hour == 1):
        print("New interval. Time: " + str(now))
        interval_tracker = now.hour
        new_interval = True

    # If the current hour matches a reset interval
    if interval_tracker in reset_intervals and now.minute >= interval_reset_minute and new_interval:
        print("Clearing list")
        new_interval = False
        members_married.clear()

    message = ctx.content
    for marriage_message in marriage_messages:
        if marriage_message in message:
            name = extract_name(message)
            print("Adding " + name)
            members_married.append(name)

    await bot.process_commands(ctx)


async def set_historical_claims():
    global text_channel
    global FILTER_INACTIVE
    global members_with_claims
    global marriage_messages
    global interval_tracker

    now = datetime.utcnow()
    day = now.day
    interval_hour = get_interval()
    if interval_hour == reset_intervals[len(reset_intervals) - 1]:
        day = (now + timedelta(days = -1)).day
    print("Interval hour: " + str(interval_hour))
    window = datetime(now.year, now.month, day, interval_hour, interval_reset_minute)
    print("Window: " + str(window))

    messages = await text_channel.history(limit = 4000, after = window, oldest_first = True).flatten()

    bot_messages = list(filter(lambda m: m.author.bot == True, messages))
    #messages_content = list(([m.content, m.created_at] for m in bot_messages)) uncomment for multiple attributes if needed
    messages_content = list(m.content for m in bot_messages)

    #print(*messages_content)

    for message in messages_content:
        for marriage_message in marriage_messages:
            if marriage_message in message:
                members_married.append(extract_name(message))


@bot.command(name='cl', help="The shortened version of the " + str(bot.command_prefix) + "claims command", case_insensitive=True)
async def print_claims_short(ctx):
    await print_claims(ctx)


# Construct response from claims messages
@bot.command(name='claims', help="See who has claims left on this rotation", case_insensitive=True)
async def print_claims(ctx):
    members_with_claims = get_claims()
    s = "\n"

    embed = discord.Embed(color=0x424c66)
    embed.title = "People with :clam:" 
    embed.description = s.join(members_with_claims)

    if len(members_with_claims) > 0:
        #print(*members_with_claims)
        await ctx.send(embed=embed)
    else:
        #print("All claimed")
        await ctx.send("Everyone's claimed for this interval!")


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


def get_interval():
    global interval_reset_minute
    global reset_intervals
    global now

    now = datetime.utcnow()

    # Cycle through each reset interval and check if the current hour is less than it
    # If it is, use the previous hour as the after window for message searching
    for i in range(len(reset_intervals)):

        print("Checking window: " + str(reset_intervals[i]))

        # Once we reach an interval that's greater than the current time, we're in the right interval
        if now.hour < reset_intervals[i]:
            return reset_intervals[i - 1]

        elif now.hour > 22:
            return reset_intervals[len(reset_intervals) - 1]

        elif now.hour == reset_intervals[i]:
            # If we're in the same hour as the interval reset but before the actual reset, use the previous interval's hour
            if now.minute < interval_reset_minute:
                if i == 0:
                    return reset_intervals[len(reset_intervals) - 1]
                else:
                    return reset_intervals[i - 1]

            else:
                return now.hour

    print("Error finding interval")


def extract_name(message):
    left = get_index(message, "**", 1) + 2 # Add two for bold markdown
    right = get_index(message, "**", 2)
    member = message[left:right]
    return member.strip()


def get_index(input_string, sub_string, ordinal):
    current = -1
    for i in range(ordinal):
        current = input_string.index(sub_string, current + 1)

    return current


def get_claims():
    # Find anyone not in the list
    members_with_claims = list(set(members) - set(members_married))

    if (FILTER_INACTIVE):
        members_with_claims = list(set(members_with_claims) - set(inactive_users))

    return sorted(members_with_claims, key = str.casefold)


bot.run(TOKEN)