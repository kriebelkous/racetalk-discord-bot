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