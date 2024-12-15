# bot.py
import asyncio
import json
import logging
import os
from datetime import date, datetime, time
from pathlib import Path

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from MyBot import MyBot

####################################################
# bot environment setup
####################################################

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# all intents set to true here must be enabled in the developer portal when inviting the bot
intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix="/", intents=intents)
logger = logging.getLogger("discord")

####################################################
# bot internal setup
####################################################


@bot.event
async def on_ready():
    """
    initial setup when bot is ready.

    1. load all book suggestions from files
    2. find all suggestion messages stored in the files
    3. wait until the time is right and the start the monday message loop
    """
    logger.info(f"We have logged in as {bot.user}")

    # get book-suggestions channels from all guilds
    book_suggestions = [discord.utils.get(
        guild.text_channels, name="book-suggestions"
    ) for guild in bot.guilds]
    logger.info(f"book_suggestions: {book_suggestions}")

    # from all book-suggestions channels load all suggestion messages
    # this could be used to check for completed suggestions
    # for each suggestion file stored
    for suggestion_file in Path("./data/").glob("suggestion*"):
        suggestion_data = json.loads(suggestion_file.read_text())
        # check whether suggestion can be loaded from any book-suggestions channel
        for channel in book_suggestions:
            try:
                suggestion_message = await channel.fetch_message(
                    suggestion_data["suggestion_message"]
                )
                logger.info(f"Monitoring reactions for message: {suggestion_message.embeds[0].description.split('\n')[-1]}")
            except Exception as e:
                logger.warning(f"Could not fetch message: {e}")

    logger.info(f"guilds the bot is a member of {bot.guilds}")
    
    # wait until the time is right. then start the monday message loop
    # 
    # this doesnt block the bot and could be used to sleep till a specific time
    # at that time, a 24 hour loop can be started, which checks whether its monday
    # each monday, guides are asked to give new info
    diff = datetime.combine(date.today(), time(12, 00)) - datetime.now()
    await asyncio.sleep(diff.seconds)
    logger.info("starting monday message loop")

    # Start the task when the time is ready
    send_monday_message.start()


####################################################
# bot welcome
####################################################


async def welcome(member):
    """
    Code to execute when a new member joins
    args:
        member: is the discord.Member object representing the new user
    """
    introductions = discord.utils.get(
        member.guild.text_channels, name="introductions"
    )
    await member.guild.system_channel.send(
        f"Welcome {member.mention}!\nplease introduce yourself in {introductions.mention}"
    )


@bot.event
async def on_member_join(member):
    """
    this should be executed when a new member joins. for some reason it doesnt work...
    args:
        member: is the discord.Member object representing the new user
    """
    await welcome(member)
    logger.info("greeted new user")


@bot.command(name="bitterblues_welcome_test", hidden=True)
async def welcome_command(ctx, *args):
    """
    this command test the welcome message
    args:
        ctx: context
        args: we ignore this
    """
    member = ctx.author
    await welcome(member)

@tasks.loop(hours=24)
async def send_monday_message():
    """
    check whether its monday. if so, 
    send the monday message to all chats in the current reads category
    """
    # if today is not monday
    if date.today().weekday() != 0:
        logger.info("today is not monday: skipping monday message")
        return
        
    # bitterblues playground: 1312810973425565746
    # book nook: 1294998125106167879
    guild = bot.get_guild(1294998125106167879)
    category = discord.utils.get(guild.categories, name="Current Reads")
    for channel in category.text_channels:
        await channel.send("this is a friendly reminder for this channels guides to update the reading goal :D")
        logger.info(f"sending monday message to guild {guild} in channel {channel}")


bot.run(TOKEN)
