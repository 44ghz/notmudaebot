# bot.py
import os
import random
import discord
import time

from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('CHANNEL')

client = discord.Client()
bot = commands.Bot(command_prefix='$$')
text_channel = ""

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(guild)
        for channel in guild.text_channels:
            print(channel.id)
            if channel.id != CHANNEL:
                text_channel = channel
    print("NotMudae is connected to Discord!")

@bot.command(name='cl', help="The shortened version of the $$claims command", case_insensitive=True)
async def get_claims_short(ctx):
    await get_claims(ctx)

# Construct response from claims messages
@bot.command(name='claims', help="See who has claims left on this rotation", case_insensitive=True)
async def get_claims(ctx):
    difference = datetime.utcnow().time().hour % 3
    interval_difference = datetime.utcnow() + timedelta(hours = difference)
    window = datetime(interval_difference.year, interval_difference.month, interval_difference.day, interval_difference.hour, 23)

    messages = await channel.history().flatten()
    bot_messages = list(filter(lambda m: m.author.bot == True, messages))
    messages_content = list((m.content for m in bot_messages))
    
    await ctx.send(text_channel)

bot.run(TOKEN)
