import random
import re
from logger.logger import get_logger
from database.database import get_triggers

logger = get_logger("Triggers")

class TriggerProcessor:
    def __init__(self):
        self.triggers = get_triggers()

    def process(self, message):
        content = message.content.lower()
        user_id = str(message.author.id)
        for trig in self.triggers:
            match_type = trig.get("match", "both")
            responses = trig.get("responses", [])
            user_overrides = trig.get("user_overrides", {})
            method = trig.get("method", "random")
            is_regex = trig.get("is_regex", False)  # New flag for regex support

            for word in trig.get("words", []):
                matched = False
                if is_regex:
                    # Treat word as a regex pattern
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
                    # Original non-regex matching
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