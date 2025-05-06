import os
from flask import Flask, redirect, request, session, url_for
from flask_session import Session
import requests
from dotenv import load_dotenv

from config.logging import get_logger
from config.config import FLASK_PORT, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, DISCORD_TOKEN, GUILD_ID, REQUIRED_ROLE_ID

logger = get_logger("flask_app")
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DISCORD_API_BASE_URL = "https://discord.com/api"
OAUTH_AUTHORIZE_URL = f"{DISCORD_API_BASE_URL}/oauth2/authorize"
OAUTH_TOKEN_URL = f"{DISCORD_API_BASE_URL}/oauth2/token"

@app.route("/")
def health():
    logger.debug("Health endpoint called.")
    if "discord_user" not in session:
        logger.info("User not in session; redirecting to login.")
        return redirect(url_for("login"))

    user = session["discord_user"]
    logger.debug(f"User from session: {user}")
    
    member = get_guild_member(user["id"])
    if not member:
        logger.warning(f"User {user['id']} is not a member of the guild.")
        return "You are not a member of the server.", 403

    role_ids = member.get("roles", [])
    if REQUIRED_ROLE_ID not in role_ids:
        logger.warning(f"User {user['id']} lacks required role {REQUIRED_ROLE_ID}.")
        return "Access denied: You do not have the required role.", 403

    logger.info(f"User {user['username']}#{user['discriminator']} accessed the bot.")
    return f"Bot is running! Welcome, {user['username']}#{user['discriminator']}", 200

@app.route("/login")
def login():
    logger.info("Redirecting to Discord OAuth2 login.")
    return redirect(
        f"{OAUTH_AUTHORIZE_URL}?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20guilds.members.read"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    logger.debug(f"OAuth callback with code: {code}")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds.members.read"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        r = requests.post(OAUTH_TOKEN_URL, data=data, headers=headers)
        r.raise_for_status()
        token = r.json()["access_token"]
        logger.info("OAuth token retrieved successfully.")
    except Exception as e:
        logger.exception("Failed to get OAuth token")
        return "OAuth token exchange failed", 500

    try:
        user_data = requests.get(
            f"{DISCORD_API_BASE_URL}/users/@me",
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        session["discord_user"] = user_data
        logger.info(f"Logged in user: {user_data}")
    except Exception as e:
        logger.exception("Failed to retrieve user data")
        return "Failed to retrieve user data", 500

    return redirect(url_for("health"))

@app.route("/logout")
def logout():
    logger.info("User logged out.")
    session.clear()
    return redirect(url_for("health"))

def get_guild_member(user_id):
    logger.debug(f"Fetching guild member for user_id: {user_id}")
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(
            f"{DISCORD_API_BASE_URL}/guilds/{GUILD_ID}/members/{user_id}",
            headers=headers
        )
        if r.status_code == 200:
            logger.debug("Guild member found.")
            return r.json()
        logger.warning(f"Guild member not found: {r.status_code} - {r.text}")
    except Exception as e:
        logger.exception("Exception fetching guild member")

    return None

if __name__ == "__main__":
    logger.info("Starting Flask app...")
    if os.getenv("ENV") != "production":
        app.run(host="0.0.0.0", port=FLASK_PORT)
