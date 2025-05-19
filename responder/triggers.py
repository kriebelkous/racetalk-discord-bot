from database import get_triggers
from logger.logger import get_logger
import re
import random

logger = get_logger("TriggerProcessor")

class TriggerProcessor:
    def __init__(self):
        self.triggers = []
        self.load_triggers()

    def load_triggers(self):
        """Load triggers from the database."""
        try:
            self.triggers = get_triggers()
            logger.info(f"Loaded {len(self.triggers)} triggers")
        except Exception as e:
            logger.error(f"Failed to load triggers: {e}")
            self.triggers = []

    def reload_triggers(self):
        """Reload triggers from the database."""
        self.load_triggers()
        logger.info("Triggers reloaded")

    def process(self, message):
        content = message.content.lower()
        user_id = str(message.author.id)
        for trig in self.triggers:
            match_type = trig.get("match", "both")
            responses = trig.get("responses", [])
            user_overrides = trig.get("user_overrides", {})
            method = trig.get("method", "random")
            is_regex = trig.get("is_regex", False)

            for word in trig.get("words", []):
                matched = False
                if is_regex:
                    try:
                        if match_type == "both":
                            matched = bool(re.search(word, content))
                        elif match_type == "sentence":
                            matched = any(bool(re.search(word, w)) for w in content.split())
                        elif match_type == "word":
                            matched = bool(re.fullmatch(word, content))
                    except re.error as e:
                        logger.error(f"Invalid regex pattern '{word}': {e}")
                        continue
                else:
                    matched = (
                        (match_type == "both" and word in content) or
                        (match_type == "sentence" and word in content.split()) or
                        (match_type == "word" and content == word)
                    )

                if matched:
                    user_resp = user_overrides.get(user_id)
                    if user_resp:
                        return random.choice(user_resp) if method == "random" else user_resp[0]
                    return random.choice(responses) if method == "random" else responses[0]
        return None