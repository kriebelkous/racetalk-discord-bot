def check_triggers(content):
    words = content.split()
    if "banaan" in words:
        return "Nog steeds bevroren?"
    if "auto" in words:
        return "Auto doet vroem vroem"
    if "cola" in words:
        return "voor de kleur"
    if len(words) == 1 and words[0] == "kutbot":
        return "https://www.gifcen.com/wp-content/uploads/2022/03/middle-finger-gif-16.gif"
    if "infrastructuur" in words and len(words) > 1:
        return "mooi in een zin verwerkt zeg"
    return None