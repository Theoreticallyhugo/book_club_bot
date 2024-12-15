import logging
import os

from discord.ext import commands

logger = logging.getLogger("discord")


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        # Call the parent class's __init__ method
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        # This method runs when the bot is starting up
        await self.load_extensions()

    async def load_extensions(self):
        """
        Automatically load all cogs in the 'cogs' directory.
        Assumes cogs are Python files with a setup function.
        """
        # Iterate through all files in the 'cogs' directory
        for filename in os.listdir("./cogs"):
            # Check if the file is a Python file
            if filename.endswith(".py"):
                # Remove the .py extension to get the module name
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    # Load the extension
                    await self.load_extension(cog_name)
                    logger.info(f"Loaded extension {cog_name}")
                except Exception as e:
                    logger.info(
                        f"Failed to load extension {cog_name}. Error: {e}"
                    )
