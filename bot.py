import discord
from discord.ext import commands
import asyncio
from usersync.user_sync import sync_users
from responder.triggers import TriggerProcessor
from logger.logger import get_logger
from config.config import SYNC_INTERVAL_MINUTES
import os
import time

logger = get_logger("Bot")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
trigger_processor = TriggerProcessor()
SIGNAL_FILE = "trigger_signal"

async def monitor_signal_file():
    """Background task to monitor signal file for trigger reload."""
    last_mtime = 0
    if not os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE, "w") as f:
            pass  # Create empty signal file
    while True:
        try:
            mtime = os.path.getmtime(SIGNAL_FILE)
            if mtime > last_mtime:
                logger.info("Detected trigger signal file change, reloading triggers")
                trigger_processor.reload_triggers()
                last_mtime = mtime
        except Exception as e:
            logger.error(f"Error monitoring signal file: {e}")
        await asyncio.sleep(1)  # Check every second

async def periodic_sync():
    """Background task to sync users periodically."""
    while True:
        try:
            for guild in bot.guilds:
                await sync_users(guild)
                logger.info(f"Completed user sync for guild: {guild.name}")
        except Exception as e:
            logger.error(f"Error during periodic sync: {e}")
        await asyncio.sleep(SYNC_INTERVAL_MINUTES * 60)

@bot.event
async def on_ready():
    logger.info(f"Bot connected as {bot.user}")
    for guild in bot.guilds:
        await sync_users(guild)
    bot.loop.create_task(periodic_sync())
    bot.loop.create_task(monitor_signal_file())  # Start signal file monitor

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    response = trigger_processor.process(message)
    if response:
        await message.channel.send(response)
    await bot.process_commands(message)

if __name__ == "__main__":
    from config.config import DISCORD_TOKEN
    bot.run(DISCORD_TOKEN)