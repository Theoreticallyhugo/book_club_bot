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

MONITORED_MESSAGES = []

####################################################
# bot internal setup
####################################################


async def load_extensions(bot):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    logger.info("loaded PollsCog")
    # This ensures the cog is loaded when the bot starts


@bot.event
async def on_ready():
    global MONITORED_MESSAGES
    logger.info(f"We have logged in as {bot.user}")

    # load suggestions in book-suggestions
    book_suggestions = [discord.utils.get(
        guild.text_channels, name="book-suggestions"
    ) for guild in bot.guilds]
    logger.info(f"book_suggestions: {book_suggestions}")

    for suggestion_file in Path("./data/").glob("suggestion*"):
        suggestion_data = json.loads(suggestion_file.read_text())
        for channel in book_suggestions:
            try:
                MONITORED_MESSAGES.append(await channel.fetch_message(
                    suggestion_data["suggestion_message"]
                ))
                logger.info(f"Monitoring reactions for message: {MONITORED_MESSAGES[-1].embeds[0].description.split('\n')[-1]}")
            except Exception as e:
                logger.warning(f"Could not fetch message: {e}")

    logger.info(f"guilds the bot is a member of {bot.guilds}")
    
    # this doesnt block the bot and could be used to sleep till a specific time
    # at that time, a 24 hour loop can be started, which checks whether its monday
    # each monday, guides are asked to give new info
    #
    # @tasks.loop(hours=24)
    # async def send_monday_message():
    #    pass
    #
    # Start the task when the time is ready
    # send_monday_message.start()
    # 
    # not sure about this one
    # Handle task cancellation when the bot is stopped
    # @send_monday_message.before_loop
    # async def before_send_monday_message():
    #     await bot.wait_until_ready()
    diff = datetime.combine(date.today(), time(12, 31)) - datetime.now()
    await asyncio.sleep(diff.seconds)
    logger.info("starting monday message loop")

    # Start the task when the time is ready
    send_monday_message.start()


####################################################
# bot welcome
####################################################


async def welcome(member):
    # Code to execute when a new member joins
    # member is the discord.Member object representing the new user
    introductions = discord.utils.get(
        member.guild.text_channels, name="introductions"
    )
    await member.guild.system_channel.send(
        f"Welcome {member.mention}!\nplease introduce yourself in {introductions.mention}"
    )


@bot.event
async def on_member_join(member):
    await welcome(member)


@bot.command(name="bitterblues_welcome_test", hidden=True)
async def welcome_command(ctx, *args):
    """
    This is a description of the command that will show in help.

    :param arg1: Description of the first argument
    :param arg2: Description of the second argument
    """
    member = ctx.author
    await welcome(member)

@tasks.loop(hours=24)
async def send_monday_message():
    # if today is not monday
    if date.today().weekday() != 0:
        logger.info("today is not monday: skipping monday message")
        return
        
    # bitterblues playground: 1312810973425565746
    guild = bot.get_guild(1312810973425565746)
    category = discord.utils.get(guild.categories, name="Current Reads")
    for channel in category.text_channels:
        await channel.send("this is a friendly reminder for this channels guides to update the reading goal :D")
        logger.info(f"sending monday message to guild {guild} in channel {channel}")


####################################################
# bot help
####################################################


async def custom_help(ctx, *args):
    message_embed = discord.Embed(
        title=f"Help",
        description="**to learn more about specific commands, write `/command help`**\n"
        + "## Polls:\n"
        + "Use /poll to create a new poll, and /pollresults "
        + "(in the same chat as the original poll) to get the respective results.\n",
    )
    await ctx.send(embed=message_embed)


# @bot.command(name="poll")
# async def intro(ctx, *, args):
#     await ctx.send(f"poll by {ctx.author.mention}\n\n{args}")

# @bot.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#
#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')

# @bot.command(name="poll")
# async def poll(ctx, title ,*args):
#     await ctx.send(f"{title}\npoll by {ctx.author.mention}\n{'\n'.join(f'{i+1}. {arg}' for i, arg in enumerate(args))}")


bot.run(TOKEN)
