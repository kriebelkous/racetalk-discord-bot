import os
from urllib.parse import quote_plus

def required_env(key):
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value

MONGO_USER = required_env("MONGO_USER")
MONGO_PASSWORD = required_env("MONGO_PASSWORD")
MONGO_HOST = required_env("MONGO_HOST")
MONGO_PORT = required_env("MONGO_PORT")
DB_NAME = required_env("DB_NAME")
DISCORD_TOKEN = required_env("DISCORD_TOKEN")

FLASK_PORT = int(required_env("FLASK_PORT"))
SYNC_INTERVAL_MINUTES = int(required_env("SYNC_INTERVAL_MINUTES"))

CLIENT_ID = required_env("DISCORD_CLIENT_ID")
CLIENT_SECRET = required_env("DISCORD_CLIENT_SECRET")
REDIRECT_URI = required_env("DISCORD_REDIRECT_URI")
GUILD_ID = required_env("DISCORD_GUILD_ID")
REQUIRED_ROLE_ID = required_env("DISCORD_REQUIRED_ROLE_ID")

MONGO_URI = (
    f"mongodb://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASSWORD)}"
    f"@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=admin"
)