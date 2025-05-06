from config.config import FLASK_PORT
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def health():
    return "Bot is running!", 200

if __name__ == "__main__":
    if os.getenv("ENV") != "production":
        app.run(host="0.0.0.0", port=FLASK_PORT)