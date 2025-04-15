import discord
from discord.ext import commands
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
import asyncio
from waitress import serve
from triggerAndResponse import check_triggers
from prefixAndResponse import setup_commands

# Configure logging
def configure_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    max_bytes = int(os.getenv('LOG_MAX_BYTES', 5 * 1024 * 1024))
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', 3))
    
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        'bot.log',
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)
    
    logging.basicConfig(
        level=numeric_level,
        handlers=[console_handler, file_handler]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level {log_level}, maxBytes={max_bytes}, backupCount={backup_count}")
    return logger

logger = configure_logging()

# Initialize Flask app
flask_app = Flask(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
# Read prefix from environment variable, default to '!' if not set
prefix = os.getenv('BOT_PREFIX', '!')
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot is ready as {bot.user} with prefix "{prefix}"')
    # Register prefix commands
    setup_commands(bot)
    logger.info("Prefix commands registered")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # Check for trigger-based responses
    response = check_triggers(message.content.lower())
    if response:
        logger.debug(f'Message triggered response: "{message.content}" -> "{response}"')
        await message.channel.send(response)
    # Process commands (e.g., !tijden or custom prefix)
    await bot.process_commands(message)

@flask_app.route('/')
def status():
    return f"<h1>Bot Status</h1><p>{bot.user} is {'Online' if bot.is_ready() else 'Offline'}</p>"

async def run_flask():
    port = int(os.getenv('FLASK_PORT', 8002))
    logger.info(f'Starting Flask server via waitress on port {port}')
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        lambda: serve(flask_app, host='0.0.0.0', port=port, threads=2)
    )

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('DISCORD_TOKEN not set')
        raise ValueError('DISCORD_TOKEN not set')
    
    try:
        flask_task = asyncio.create_task(run_flask())
        bot_task = asyncio.create_task(bot.start(token))
        await asyncio.gather(flask_task, bot_task, return_exceptions=True)
    except discord.errors.LoginFailure:
        logger.error('Failed to login to Discord: Invalid token')
        raise
    except Exception as e:
        logger.error(f'Bot or Flask encountered an error: {e}')
        raise
    finally:
        logger.info('Shutting down')
        if not bot.is_closed():
            await bot.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Received shutdown request')