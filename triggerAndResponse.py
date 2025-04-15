import random

# Store the last response for the randomtest trigger to avoid repetition
last_randomtest_response = None

# Store the current index for the sequencetest trigger
sequencetest_index = 0

def check_triggers(content):
    global last_randomtest_response, sequencetest_index
    words = content.split()
    
    # Existing triggers
    if "wildcardtest" in words:
        return "wildcardresponse"
    if len(words) == 1 and words[0] == "standalonetest":
        return "standalone response"
    if len(words) == 1 and words[0] == "sentencetest":
        return "use this keyword in a sentence"
    if "sentencetest" in words and len(words) > 1:
        return "sentencetest response"
    if "standalonetest" in words and len(words) > 1:
        return "Dont use this keyword in a sentence"
    
    # Randomtest trigger (from previous request)
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
        return chosen_response
    
    # New trigger: sequencetest
    if "sequencetest" in words:
        # Define possible responses (1 to 50; here we use 3 as an example, but you can expand)
        sequencetest_responses = [
            "response01",
            "response02",
            "response03",
            "response04"
        ]
        
        # Ensure response list length is within bounds (1 to 50)
        if not (1 <= len(sequencetest_responses) <= 50):
            return "Error: sequencetest must have between 1 and 50 responses"
        
        # Get the current response based on the index
        chosen_response = sequencetest_responses[sequencetest_index]
        
        # Update the index for the next call (cycle back to 0 if at the end)
        sequencetest_index = (sequencetest_index + 1) % len(sequencetest_responses)
        
        return chosen_response
    
    return None