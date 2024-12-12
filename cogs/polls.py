import logging

import discord
from discord.ext import commands

logger = logging.getLogger("discord")


class PollsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx, title: str, *options: str):
        """Create polls as /poll "title" "option 1" "option 2" ... "option n"

        Parameters:
        - title: 'add' or 'remove' to specify role modification
        - options: The role to be added or removed
        """

        # Validate options
        if len(options) < 2 or len(options) > 10:
            await ctx.send("Please provide between 2 and 10 poll options.")
            return

        # Create an embed for the poll
        poll_embed = discord.Embed(
            title=f"📊 Poll",
            description=f"by {ctx.author.mention}\n\n**{title}**\n\n"
            + "\n".join(
                [
                    f"{chr(127344+i)} {option}"
                    for i, option in enumerate(options)
                ]
            ),
        )
        # Send the poll message
        poll_message = await ctx.send(embed=poll_embed)

        # Add reaction options
        for i in range(len(options)):
            await poll_message.add_reaction(chr(127344 + i))

    @commands.command()
    async def pollresults(self, ctx, message_id):

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
                [f"{option}: {count} votes" for option, count in total_count]
            ),
        )

        await ctx.send(embed=results_embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        if only one vote per user is allowed, run this function.
        """
        # Ignore reactions from the bot itself
        if user == self.bot.user:
            return

        # if the message has an embedding and its title is that of a poll
        if reaction.message.embeds and reaction.message.embeds[
            0
        ].title.startswith("📊 Poll"):
            # Check if the user has already reacted
            # Get all reactions on the message
            for existing_reaction in reaction.message.reactions:
                # Check if the user has already used this specific emoji
                async for previous_user in existing_reaction.users():
                    if (
                        previous_user == user
                        and existing_reaction.emoji != reaction.emoji
                    ):
                        # Remove the previous reaction
                        await reaction.message.remove_reaction(
                            existing_reaction.emoji, user
                        )


# This is the key part for loading
async def setup(bot):
    await bot.add_cog(PollsCog(bot))
