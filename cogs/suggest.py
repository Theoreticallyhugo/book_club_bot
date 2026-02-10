import json
import logging
from pathlib import Path

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
        """
        set up a poll for a new book.

        args:
            ctx: context
            suggestion: entire text of the message, after the command
        """
        # adapt suggestion to discord channel syntax
        suggestion = suggestion.replace(" ", "-").replace(",", "")

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
        suggestion_message = await ctx.send(embed=poll_embed)

        # Add reaction option
        await suggestion_message.add_reaction(chr(128077))
        suggestion_data = {
            "author_name": ctx.author.name,
            "author_id": ctx.author.id,
            "suggestion": suggestion,
            "suggestion_message": suggestion_message.id,
        }
        Path(f"./data/suggestion_{suggestion}.json").write_text(
            json.dumps(suggestion_data)
        )

    async def fetch_message(self, guild_id, channel_id, message_id):
        """
        get a message object, based on guild, channel and message id

        args:
            guild_id: int
            channel_id: int
            message_id: int
        """
        # Get the guild (server)
        guild = self.bot.get_guild(guild_id)
        # if not guild:
        #     await ctx.send("Could not find the guild.")
        #     return

        # Get the channel
        channel = guild.get_channel(channel_id)
        # if not channel:
        #     await ctx.send("Could not find the channel.")
        #     return

        # Fetch the message
        return await channel.fetch_message(message_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        whenever any reaction is added to any message, check whether its a suggestion.
        """
        # get the user and message
        user = payload.member
        message = await self.fetch_message(
            payload.guild_id, payload.channel_id, payload.message_id
        )
        # Ignore reactions from the bot itself
        if user == self.bot.user:
            return

        logger.info(f"{user} reacted to {message.id}")

        # if the message has an embedding and its title is that of a poll
        if message.embeds and message.embeds[0].title.startswith(
            "New Book Suggestion"
        ):
            num_of_upvotes = [
                reaction.count
                for reaction in message.reactions
                if reaction.emoji == chr(128077)
            ][0]
            logger.info(
                f"its a poll and there are {num_of_upvotes} upvotes; {message.reactions}"
            )
            # if len(message.reactions) > 0:
            if num_of_upvotes > 3:
                channel_name = message.embeds[0].description.split("\n")[-1]

                # create new text channel
                guild = message.guild
                category = discord.utils.get(
                    guild.categories, name="Current Reads"
                )
                await guild.create_text_channel(
                    channel_name, category=category
                )
                new_channel = discord.utils.get(
                    message.guild.text_channels,
                    name=channel_name.replace(" ", "-"),
                )
                await message.channel.send(
                    f"created new channel {new_channel.mention}"
                )
                await message.delete()

                # file that stored the suggestion
                suggestion_file = Path(
                    f"./data/suggestion_{channel_name}.json"
                )
                suggestion_data = json.loads(suggestion_file.read_text())

                # add guides
                channel_guide_path = Path(f"./data/guides_{channel_name}.json")

                # write data with new guide
                channel_guide_path.write_text(
                    json.dumps(
                        [
                            {
                                "name": suggestion_data["author_name"],
                                "id": suggestion_data["author_id"],
                            }
                        ]
                    )
                )

                # remove suggestion file
                suggestion_file.unlink()


# This is the key part for loading
async def setup(bot):
    await bot.add_cog(SuggestCog(bot))
