import logging

import discord
from discord.ext import commands

logger = logging.getLogger("discord")


class PinCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pin(self, ctx):
        try:
            if ctx.message.reference:
                replied_to_message = await ctx.channel.fetch_message(
                    ctx.message.reference.message_id
                )
                await replied_to_message.pin()
                await ctx.send("Message pinned!")
            else:
                await ctx.send("Please reply to a message to pin it!")
        except discord.Forbidden:
            await ctx.send("I don't have permission to pin messages!")
        except discord.HTTPException:
            await ctx.send(
                "Failed to pin the message. There might be too many pinned messages already."
            )

    @commands.command()
    async def unpin(self, ctx):
        try:
            if ctx.message.reference:
                replied_to_message = await ctx.channel.fetch_message(
                    ctx.message.reference.message_id
                )
                await replied_to_message.unpin()
                await ctx.send("Message pin removed!")
            else:
                await ctx.send("Please reply to a message to unpin it!")
        except discord.Forbidden:
            await ctx.send("I don't have permission to unpin messages!")
        except discord.HTTPException:
            await ctx.send("Failed to unpin the message.")


# This is the key part for loading
async def setup(bot):
    await bot.add_cog(PinCog(bot))
