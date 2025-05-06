import discord
from discord.ext import commands
import asyncio
from usersync.user_sync import sync_users
from responder.triggers import TriggerProcessor
from logger.logger import get_logger
from config.config import SYNC_INTERVAL_MINUTES

logger = get_logger("Bot")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
trigger_processor = TriggerProcessor()

async def periodic_sync():
    """Background task to sync users periodically."""
    while True:
        try:
            for guild in bot.guilds:
                await sync_users(guild)
                logger.info(f"Completed user sync for guild: {guild.name}")
        except Exception as e:
            logger.error(f"Error during periodic sync: {e}")
        # Convert minutes to seconds for asyncio.sleep
        await asyncio.sleep(SYNC_INTERVAL_MINUTES * 60)

@bot.event
async def on_ready():
    logger.info(f"Bot connected as {bot.user}")
    # Run initial sync
    for guild in bot.guilds:
        await sync_users(guild)
    # Start the periodic sync task
    bot.loop.create_task(periodic_sync())

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    response = trigger_processor.process(message)
    if response:
        await message.channel.send(response)
    # Ensure commands still work
    await bot.process_commands(message)

if __name__ == "__main__":
    from config.config import DISCORD_TOKEN
    bot.run(DISCORD_TOKEN)