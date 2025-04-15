import discord
import logging

logger = logging.getLogger(__name__)

def check_mentions(message: discord.Message, bot_user: discord.User) -> str | None:
    """Check if the bot is mentioned and return the appropriate response."""
    # Check if the bot is mentioned
    if bot_user.id not in [mention.id for mention in message.mentions]:
        return None
    
    # Get the content after the mention (trimmed, lowercase for consistency)
    content = message.content.lower().strip()
    # Remove mentions from content to isolate text
    for mention in message.mentions:
        content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '').strip()
    
    # Hardcoded specific user ID (replace with your actual Discord user ID)
    specific_user_id = 688688081909448949  # TODO: Replace with your user ID
    
    # Handle mention responses
    if not content:
        logger.debug(f'Bot mentioned by {message.author} with no content')
        return "mention response"
    
    if content == "test":
        logger.debug(f'Bot mentioned by {message.author} with "test"')
        return "test mention response"
    
    if content == "userspecific":
        logger.debug(f'Bot mentioned by {message.author} with "userspecific"')
        if message.author.id == specific_user_id:
            return "userspecificresponse"
        return "no userspecificresponse"
    
    logger.debug(f'Bot mentioned by {message.author} with unrecognized content: "{content}"')
    return None