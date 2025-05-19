import os
import uuid
import re
from datetime import datetime
from logger.logger import get_logger
from flask import Flask, redirect, request, session, url_for, render_template, flash
from flask_session import Session
import requests
from dotenv import load_dotenv
from database import db, get_triggers, store_user
load_dotenv()

logger = get_logger("flask_app")
logger.info("Loaded imports")

from config.config import FLASK_PORT, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, DISCORD_TOKEN, GUILD_ID, REQUIRED_ROLE_ID
logger.info("Loaded config variables")

logger.info("Initializing Flask app")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DISCORD_API_BASE_URL = "https://discord.com/api"
OAUTH_AUTHORIZE_URL = f"{DISCORD_API_BASE_URL}/oauth2/authorize"
OAUTH_TOKEN_URL = f"{DISCORD_API_BASE_URL}/oauth2/token"

def validate_trigger_words(words, is_regex):
    """Validate trigger words or regex patterns."""
    if not words:
        return False, "At least one trigger word is required."
    if is_regex:
        for word in words:
            try:
                re.compile(word)
            except re.error:
                return False, f"Invalid regex pattern: {word}"
    return True, ""

def convert_condition_to_regex(word, condition):
    """Convert trigger condition to regex pattern."""
    word = re.escape(word.strip())
    if condition == "beginning":
        return f"^{word}\\b"
    elif condition == "end":
        return f"\\b{word}$"
    else:  # anywhere
        return f"\\b{word}\\b"

def get_users():
    """Fetch all users from the users collection."""
    try:
        users = list(db.users.find({}, {"id": 1, "name": 1, "_id": 0}))
        return [{"user_id": u["id"], "username": u.get("name")} for u in users]
    except Exception as e:
        logger.exception("Failed to fetch users")
        return []

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

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "discord_user" not in session:
        return redirect(url_for("login"))
    
    user = session["discord_user"]
    member = get_guild_member(user["id"])
    if not member or REQUIRED_ROLE_ID not in member.get("roles", []):
        return "Access denied.", 403

    try:
        triggers = get_triggers()
        logger.info(f"Loaded {len(triggers)} triggers for user {user['id']}")
    except Exception as e:
        logger.exception("Failed to load triggers")
        flash("Failed to load triggers.", "error")
        triggers = []

    return render_template("dashboard.html", user=user, triggers=triggers)

@app.route("/trigger/add", methods=["GET", "POST"])
def add_trigger():
    if "discord_user" not in session:
        return redirect(url_for("login"))
    
    user = session["discord_user"]
    member = get_guild_member(user["id"])
    if not member or REQUIRED_ROLE_ID not in member.get("roles", []):
        return "Access denied.", 403

    users = get_users()
    if request.method == "POST":
        trigger_words = request.form.getlist("trigger_words")
        condition = request.form.get("condition")
        match_type = request.form.get("match", "both")
        responses = request.form.getlist("responses")
        method = request.form.get("method", "random")
        is_regex = request.form.get("is_regex") == "true"
        enabled = request.form.get("enabled") == "true"
        user_override_ids = request.form.getlist("user_override_ids")
        user_override_responses = request.form.getlist("user_override_responses")

        if not is_regex:
            trigger_words = [convert_condition_to_regex(word, condition) for word in trigger_words]

        valid, error = validate_trigger_words(trigger_words, is_regex)
        if not valid:
            flash(error, "error")
            return render_template("add_trigger.html", user=user, users=users)

        if not responses:
            flash("At least one response is required.", "error")
            return render_template("add_trigger.html", user=user, users=users)

        user_overrides = {}
        if user_override_ids and user_override_responses:
            for uid, resp in zip(user_override_ids, user_override_responses):
                if uid and resp:
                    user_overrides[uid] = [resp]
                    # Ensure user is stored
                    user_data = next((u for u in users if u["user_id"] == uid), None)
                    if user_data and user_data.get("username"):
                        store_user(uid, user_data["username"])

        trigger_id = f"trig_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat() + "Z"
        trigger = {
            "_id": str(uuid.uuid4()),
            "trigger_id": trigger_id,
            "words": trigger_words,
            "match": match_type,
            "responses": responses,
            "method": method,
            "is_regex": is_regex,
            "user_overrides": user_overrides,
            "enabled": enabled,
            "created_at": now,
            "updated_at": now
        }

        try:
            db.triggers.insert_one(trigger)
            logger.info(f"Created trigger {trigger_id} by user {user['id']}")
            flash("Trigger created successfully!", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            logger.exception("Failed to create trigger")
            flash("Failed to create trigger.", "error")

    return render_template("add_trigger.html", user=user, users=users)

@app.route("/trigger/edit/<trigger_id>", methods=["GET", "POST"])
def edit_trigger(trigger_id):
    if "discord_user" not in session:
        return redirect(url_for("login"))
    
    user = session["discord_user"]
    member = get_guild_member(user["id"])
    if not member or REQUIRED_ROLE_ID not in member.get("roles", []):
        return "Access denied.", 403

    try:
        trigger = db.triggers.find_one({"trigger_id": trigger_id})
        if not trigger:
            raise ValueError("Trigger not found")
    except Exception as e:
        logger.exception(f"Trigger {trigger_id} not found")
        flash("Trigger not found.", "error")
        return redirect(url_for("dashboard"))

    users = get_users()
    if request.method == "POST":
        trigger_words = request.form.getlist("trigger_words")
        condition = request.form.get("condition")
        match_type = request.form.get("match", "both")
        responses = request.form.getlist("responses")
        method = request.form.get("method", "random")
        is_regex = request.form.get("is_regex") == "true"
        enabled = request.form.get("enabled") == "true"
        user_override_ids = request.form.getlist("user_override_ids")
        user_override_responses = request.form.getlist("user_override_responses")

        if not is_regex:
            trigger_words = [convert_condition_to_regex(word, condition) for word in trigger_words]

        valid, error = validate_trigger_words(trigger_words, is_regex)
        if not valid:
            flash(error, "error")
            return render_template("edit_trigger.html", user=user, trigger=trigger, users=users)

        if not responses:
            flash("At least one response is required.", "error")
            return render_template("edit_trigger.html", user=user, trigger=trigger, users=users)

        user_overrides = {}
        if user_override_ids and user_override_responses:
            for uid, resp in zip(user_override_ids, user_override_responses):
                if uid and resp:
                    user_overrides[uid] = [resp]
                    # Ensure user is stored
                    user_data = next((u for u in users if u["user_id"] == uid), None)
                    if user_data and user_data.get("username"):
                        store_user(uid, user_data["username"])

        updated_trigger = {
            "words": trigger_words,
            "match": match_type,
            "responses": responses,
            "method": method,
            "is_regex": is_regex,
            "user_overrides": user_overrides,
            "enabled": enabled,
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }

        try:
            db.triggers.update_one(
                {"trigger_id": trigger_id},
                {"$set": updated_trigger}
            )
            logger.info(f"Updated trigger {trigger_id} by user {user['id']}")
            flash("Trigger updated successfully!", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            logger.exception("Failed to update trigger")
            flash("Failed to update trigger.", "error")

    return render_template("edit_trigger.html", user=user, trigger=trigger, users=users)

@app.route("/trigger/delete/<trigger_id>", methods=["POST"])
def delete_trigger(trigger_id):
    if "discord_user" not in session:
        return redirect(url_for("login"))
    
    user = session["discord_user"]
    member = get_guild_member(user["id"])
    if not member or REQUIRED_ROLE_ID not in member.get("roles", []):
        return "Access denied.", 403

    try:
        result = db.triggers.delete_one({"trigger_id": trigger_id})
        if result.deleted_count == 0:
            raise ValueError("Trigger not found")
        logger.info(f"Deleted trigger {trigger_id} by user {user['id']}")
        flash("Trigger deleted successfully!", "success")
    except Exception as e:
        logger.exception(f"Failed to delete trigger {trigger_id}")
        flash("Failed to delete trigger.", "error")

    return redirect(url_for("dashboard"))

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
        # Store the logged-in user
        store_user(user_data["id"], f"{user_data['username']}#{user_data['discriminator']}")
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