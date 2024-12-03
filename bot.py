# bot.py
import os
from typing import Dict, List, Tuple

import discord
from discord.ext import commands
from dotenv import load_dotenv

from poll import Poll

####################################################
# bot environment setup
####################################################

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# all intents set to true here must be enabled in the developer portal when inviting the bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

####################################################
# bot internal setup
####################################################


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


####################################################
# bot polls
####################################################


@bot.command()
async def poll(ctx, title: str, *options: str):
    # Validate options
    if len(options) < 2 or len(options) > 10:
        await ctx.send("Please provide between 2 and 10 poll options.")
        return

    # Create an embed for the poll
    poll_embed = discord.Embed(
        title=f"📊 Poll",
        description=f"by {ctx.author.mention}\n\n**{title}**\n\n" + 
        "\n".join([f"{chr(127344+i)} {option}" for i, option in enumerate(options)])
    )
    # Send the poll message
    poll_message = await ctx.send(embed=poll_embed)

    # Add reaction options
    for i in range(len(options)):
        await poll_message.add_reaction(chr(127344 + i))

@bot.event
async def on_reaction_add(reaction, user):
    """
    if only one vote per user is allowed, run this function.
    """
    # Ignore reactions from the bot itself
    if user == bot.user:
        return

    # if the message has an embedding and its title is that of a poll
    if reaction.message.embeds and reaction.message.embeds[0].title.startswith("📊 Poll"):
        # Check if the user has already reacted
        # Get all reactions on the message
        for existing_reaction in reaction.message.reactions:
            # Check if the user has already used this specific emoji
            async for previous_user in existing_reaction.users():
                if previous_user == user and existing_reaction.emoji != reaction.emoji:
                    # Remove the previous reaction
                    await reaction.message.remove_reaction(existing_reaction.emoji, user)


@bot.command()
async def pollresults(ctx, message_id):

    # try to fetch the message to the poll
    try:
        message = await ctx.channel.fetch_message(message_id)
    except:
        await ctx.send("No poll found with that message ID.")
        return


    # if the message has an embedding and its title is that of a poll
    if message.embeds and message.embeds[0].title.startswith("📊 Poll"):
        # parse options here 
        description = message.embeds[0].description.split("\n")
        title = description[2]
        options = description[4:]
    else:
        await ctx.send("No poll found with that message ID.")
        return
            

    total_count = []
    for i, option in enumerate(options):
        for reaction in message.reactions:
            if str(reaction.emoji) == chr(127344 + i):
                total_count.append((option, reaction.count - 1))

    # Create results embed
    results_embed = discord.Embed(
        title="📊 Poll Results",
        description=f"**{title}**\n\n"
        + "\n".join(
            [
                f"{option}: {count} votes"
                for option, count in total_count
            ]
        ),
    )

    await ctx.send(embed=results_embed)


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
