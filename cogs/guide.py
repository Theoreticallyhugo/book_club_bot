import json
import logging
from pathlib import Path

import discord
from discord.ext import commands

logger = logging.getLogger("discord")


class GuideCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def make_guide(self, ctx, member: discord.Member):
        """
        If user is an Admin, make member a guide for the current channel.
        """

        # get the admin role
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")

        # Check if the author has the Admin role
        if admin_role in ctx.author.roles:
            await ctx.send(f"You have the Admin role! granting channel_guide to {member.name} with id {member.id}")
            # the admin-only command logic here
            current_channel = ctx.message.channel
            channel_guide_path = Path(f"./data/guides_{current_channel}.json")

            # get existing guides if there are any
            channel_guides = []
            if channel_guide_path.is_file():
                channel_guides = json.loads(channel_guide_path.read_text())

            # add new guide
            channel_guides.append({
                "name": member.name,
                "id": member.id,
                })
            
            # write data with new guide
            channel_guide_path.write_text(json.dumps(channel_guides))
            

        else:
            await ctx.send(f"You don't have permission to use this command. unable to grant channel_guide to {member.name} with id {member.id}")

    @commands.command()
    async def remove_guide(self, ctx, member: discord.Member):
        """
        If user is an Admin, remove member as guide for the current channel.
        """

        # get the admin role
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")

        # Check if the author has the Admin role
        if admin_role in ctx.author.roles:
            await ctx.send(f"You have the Admin role! removeing channel_guide from {member.name} with id {member.id}")
            # the admin-only command logic here
            current_channel = ctx.message.channel
            channel_guide_path = Path(f"./data/guides_{current_channel}.json")

            # get existing guides if there are any
            channel_guides = []
            if channel_guide_path.is_file():
                channel_guides = json.loads(channel_guide_path.read_text())

            # remove member as guide
            for i, guide in enumerate(channel_guides):
                if guide["id"] == member.id:
                    channel_guides.pop(i)
                    break
            
            # write data without guide
            channel_guide_path.write_text(json.dumps(channel_guides))
            

        else:
            await ctx.send(f"You don't have permission to use this command. unable to remove channel_guide from {member.name} with id {member.id}")

    @commands.command()
    async def show_guides(self, ctx):
        """
        Show all guides
        """
        # the admin-only command logic here
        current_channel = ctx.message.channel
        channel_guide_path = Path(f"./data/guides_{current_channel}.json")

        # get existing guides if there are any
        channel_guides = []
        if channel_guide_path.is_file():
            channel_guides = json.loads(channel_guide_path.read_text())
            guides = [f"{guide['name']}: {guide['id']}" for guide in channel_guides]
            await ctx.send(f"Channel {current_channel} has guides:\n{'\n'.join(guides)}")
        else:
            await ctx.send(f"Channel {current_channel} has no guides.")



# This is the key part for loading
async def setup(bot):
    await bot.add_cog(GuideCog(bot))
