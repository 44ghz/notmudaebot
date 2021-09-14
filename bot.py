# bot.py
import os
import random
import discord

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$$')

@bot.command(name='cl', help="The shortened version of the $$claims command")
async def getClaimsShort(ctx):
    await getClaims(ctx)

# Construct response from claims messages
@bot.command(name='claims', help="See who has claims left on this rotation")
async def getClaims(ctx):
    allmessages = await channel.history(after=time).flatten().find(lambda m: m.author.bot == true)
    messages = dicord.util.get(allmessages, bot == true)
    await ctx.send(response)

bot.run(TOKEN)
