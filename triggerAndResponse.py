def check_triggers(content):
    words = content.split()
    if "banaan" in words:
        return "Nog steeds bevroren?"
    if "auto" in words:
        return "Auto doet vroem vroem"
    if "cola" in words:
        return "voor de kleur"
    if len(words) == 1 and words[0] == "tijden":
        return "hier zijn de tijden"
    if "infrastructuur" in words and len(words) > 1:
        return "mooi in een zin verwerkt zeg"
    return None