from database.database import store_user
from logger.logger import get_logger

logger = get_logger("UserSync")

async def sync_users(guild):
    logger.info(f"Syncing users for guild: {guild.name}")
    for member in guild.members:
        display_name = member.nick if member.nick else member.name
        store_user(member.id, display_name)
