import random
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
            
            for word in trig.get("words", []):
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
