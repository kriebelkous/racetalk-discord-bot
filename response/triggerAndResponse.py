import random

# Store the last response for the randomtest trigger to avoid repetition
last_randomtest_response = None

# Store the current index for the sequencetest trigger
sequencetest_index = 0

def check_triggers(message):
    global last_randomtest_response, sequencetest_index
    
    # Hardcoded specific user ID (replace with your actual Discord user ID)
    specific_user_id = 688688081909448949  # TODO: Replace with your user ID
    
    # Extract content and author from message
    content = message.content.lower()
    author_id = message.author.id
    words = content.split()
    
    # Check if the author is the specific user
    is_specific_user = author_id == specific_user_id
    
    # Triggers with user-specific responses
    if "wildcardtest" in words:
        return "wildcardresponse (special)" if is_specific_user else "wildcardresponse"
    
    if len(words) == 1 and words[0] == "standalonetest":
        return "standalone response (special)" if is_specific_user else "standalone response"
    
    if len(words) == 1 and words[0] == "sentencetest":
        return "use this keyword in a sentence (special)" if is_specific_user else "use this keyword in a sentence"
    
    if "sentencetest" in words and len(words) > 1:
        return "sentencetest response (special)" if is_specific_user else "sentencetest response"
    
    if "standalonetest" in words and len(words) > 1:
        return "Dont use this keyword in a sentence (special)" if is_specific_user else "Dont use this keyword in a sentence"
    
    # Randomtest trigger
    if "randomtest" in words:
        randomtest_responses = [
            "response01",
            "response02",
            "response03",
            "response04"
        ]
        if not (2 <= len(randomtest_responses) <= 50):
            return "Error: randomtest must have between 2 and 50 responses"
        available_responses = [
            resp for resp in randomtest_responses 
            if resp != last_randomtest_response
        ]
        if not available_responses:
            available_responses = randomtest_responses
        chosen_response = random.choice(available_responses)
        last_randomtest_response = chosen_response
        return f"{chosen_response} (special)" if is_specific_user else chosen_response
    
    # Sequencetest trigger
    if "sequencetest" in words:
        sequencetest_responses = [
            "response01",
            "response02",
            "response03",
            "response04"
        ]
        
        if not (1 <= len(sequencetest_responses) <= 50):
            return "Error: sequencetest must have between 1 and 50 responses"
        
        chosen_response = sequencetest_responses[sequencetest_index]
        sequencetest_index = (sequencetest_index + 1) % len(sequencetest_responses)
        return f"{chosen_response} (special)" if is_specific_user else chosen_response
    
    return None