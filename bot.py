# bot.py
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

import discord
from discord.ext import commands
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
