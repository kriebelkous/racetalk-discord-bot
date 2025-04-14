import discord
from discord.ext import commands
import os
import logging
from logging.handlers import RotatingFileHandler
from gunicorn.app.base import BaseApplication
from flask import Flask
import threading
import sys
from triggerAndResponse import check_triggers

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
bot = commands.Bot(command_prefix='!', intents=intents)

# Shutdown event
shutdown_event = threading.Event()

@bot.event
async def on_ready():
    logger.info(f'Bot is ready as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    response = check_triggers(message.content.lower())
    if response:
        logger.debug(f'Message triggered response: "{message.content}" -> "{response}"')
        await message.channel.send(response)
    await bot.process_commands(message)

@flask_app.route('/')
def status():
    return f"<h1>Bot Status</h1><p>{bot.user} is {'Online' if bot.is_ready() else 'Offline'}</p>"

class GunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def run_gunicorn():
    port = int(os.getenv('FLASK_PORT', 8000))
    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': 2,
        'loglevel': 'info',
        'accesslog': '-',
        'errorlog': '-'
    }
    logger.info(f'Starting Gunicorn on port {port}')
    gunicorn_app = GunicornApp(flask_app, options)
    try:
        gunicorn_app.run()
    except Exception as e:
        logger.error(f'Gunicorn failed: {e}')
        shutdown_event.set()
    finally:
        logger.info('Gunicorn thread stopped')
        shutdown_event.set()

def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('DISCORD_TOKEN not set')
        raise ValueError('DISCORD_TOKEN not set')
    
    gunicorn_thread = threading.Thread(target=run_gunicorn)
    gunicorn_thread.start()
    
    try:
        logger.info('Starting Discord bot')
        bot.run(token)
    except discord.errors.LoginFailure:
        logger.error('Failed to login to Discord: Invalid token')
        shutdown_event.set()
        raise
    except KeyboardInterrupt:
        logger.info('Received shutdown request')
        shutdown_event.set()
        bot.loop.create_task(bot.close())
    except Exception as e:
        logger.error(f'Bot encountered an error: {e}')
        shutdown_event.set()
        raise
    finally:
        logger.info('Bot shutting down')
        shutdown_event.set()
        gunicorn_thread.join(timeout=5.0)
        if gunicorn_thread.is_alive():
            logger.warning('Gunicorn thread did not stop gracefully')
        sys.exit(0)

if __name__ == '__main__':
    main()