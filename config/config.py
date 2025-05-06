import os
from urllib.parse import quote_plus

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DB_NAME = os.getenv("DB_NAME")
FLASK_PORT = int(os.getenv("FLASK_PORT"))
MONGO_URI = f"mongodb://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASSWORD)}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=admin"

# variables for the admin panel login

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")    # Your server's ID
REQUIRED_ROLE_ID = os.getenv("DISCORD_REQUIRED_ROLE_ID")  # The role ID users must have

# Define the sync interval (in minutes) for the user sync to database
SYNC_INTERVAL_MINUTES = int(os.getenv("SYNC_INTERVAL_MINUTES"))