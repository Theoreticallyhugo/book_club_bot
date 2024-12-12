import logging
from datetime import datetime
from pathlib import Path
import json

import discord
from discord.ext import commands

####################################################
# bot new channel
####################################################

logger = logging.getLogger("discord")


class SuggestCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        book_suggestions = discord.utils.get(
            ctx.message.guild.text_channels,
            name="book-suggestions",
        )

        if ctx.message.channel != book_suggestions:
            await ctx.send(
                f"you may only suggest a book in {book_suggestions.mention}"
            )
            return

        # Create an embed for the poll
        poll_embed = discord.Embed(
            title=f"New Book Suggestion:",
            description=f"{ctx.author.mention} suggests:\n\n{suggestion}",
        )

        # Send the poll message
        poll_message = await ctx.send(embed=poll_embed)

        # Add reaction option
        await poll_message.add_reaction(chr(128077))
        suggestion_data = {
            "author_name": ctx.author.name,
            "author_id": ctx.author.id,
            "suggestion": suggestion,
            "poll_message": poll_message.id,
            }
        Path(f"./data/suggestion{datetime.now():%Y-%m-%d_%H:%M:%S}").write_text(json.dumps(suggestion_data))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore reactions from the bot itself
        if user == self.bot.user:
            return

        # if the message has an embedding and its title is that of a poll
        if reaction.message.embeds and reaction.message.embeds[
            0
        ].title.startswith("New Book Suggestion"):
            # if len(reaction.message.reactions) > 2:
            if len(reaction.message.reactions) > 0:
                channel_name = reaction.message.embeds[0].description.split(
                    "\n"
                )[-1]

                # create new text channel
                guild = reaction.message.guild
                category = discord.utils.get(
                    guild.categories, name="Current Reads"
                )
                await guild.create_text_channel(
                    channel_name, category=category
                )
                new_channel = discord.utils.get(
                    reaction.message.guild.text_channels,
                    name=channel_name.replace(" ", "-"),
                )
                await reaction.message.channel.send(
                    f"created new channel {new_channel.mention}"
                )
                await reaction.message.delete()


# This is the key part for loading
async def setup(bot):
    await bot.add_cog(SuggestCog(bot))
