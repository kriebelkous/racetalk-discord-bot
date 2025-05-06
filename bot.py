import discord
from discord.ext import commands
from usersync.user_sync import sync_users
from responder.triggers import TriggerProcessor
from logger.logger import get_logger

logger = get_logger("Bot")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
trigger_processor = TriggerProcessor()

@bot.event
async def on_ready():
    logger.info(f"Bot connected as {bot.user}")
    for guild in bot.guilds:
        await sync_users(guild)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    response = trigger_processor.process(message)
    if response:
        await message.channel.send(response)

if __name__ == "__main__":
    from config.config import DISCORD_TOKEN
    bot.run(DISCORD_TOKEN)
