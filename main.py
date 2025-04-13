import discord
from discord.ext import commands
import os
import certifi
from flask import Flask
import threading
from triggerAndResponse import check_triggers

# Initialize Flask app
flask_app = Flask(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    response = check_triggers(message.content.lower())
    if response:
        await message.channel.send(response)
    await bot.process_commands(message)

@flask_app.route('/')
def status():
    return f"<h1>Bot Status</h1><p>{bot.user} is {'Online' if bot.is_ready() else 'Offline'}</p>"

def run_flask():
    port = int(os.getenv('FLASK_PORT', 8000))
    flask_app.run(host='0.0.0.0', port=port)

def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN not set")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    bot.run(token)

if __name__ == "__main__":
    main()