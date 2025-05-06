from config.config import FLASK_PORT, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, DISCORD_TOKEN, GUILD_ID, REQUIRED_ROLE_ID
from flask import Flask, redirect, request, session, url_for
from flask_session import Session
import requests
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DISCORD_API_BASE_URL = "https://discord.com/api"
OAUTH_AUTHORIZE_URL = f"{DISCORD_API_BASE_URL}/oauth2/authorize"
OAUTH_TOKEN_URL = f"{DISCORD_API_BASE_URL}/oauth2/token"

@app.route("/")
def health():
    if "discord_user" not in session:
        return redirect(url_for("login"))

    user = session["discord_user"]
    member = get_guild_member(user["id"])

    if not member:
        return "You are not a member of the server.", 403

    role_ids = member.get("roles", [])
    if REQUIRED_ROLE_ID not in role_ids:
        return "Access denied: You do not have the required role.", 403

    return f"Bot is running! Welcome, {user['username']}#{user['discriminator']}", 200

@app.route("/login")
def login():
    return redirect(
        f"{OAUTH_AUTHORIZE_URL}?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20guilds.members.read"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds.members.read"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(OAUTH_TOKEN_URL, data=data, headers=headers)
    r.raise_for_status()
    token = r.json()["access_token"]

    user_data = requests.get(
        f"{DISCORD_API_BASE_URL}/users/@me",
        headers={"Authorization": f"Bearer {token}"}
    ).json()

    session["discord_user"] = user_data
    return redirect(url_for("health"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("health"))

def get_guild_member(user_id):
    """Get member info from the guild using bot token."""
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.get(
        f"{DISCORD_API_BASE_URL}/guilds/{GUILD_ID}/members/{user_id}",
        headers=headers
    )
    if r.status_code == 200:
        return r.json()
    return None

if __name__ == "__main__":
    if os.getenv("ENV") != "production":
        app.run(host="0.0.0.0", port=FLASK_PORT)
