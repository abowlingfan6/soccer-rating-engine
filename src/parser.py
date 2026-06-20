def get_position(pos):
    if pos is None:
        return "Sub"

    pos = str(pos).upper().strip()

    if "DF" in pos:
        return "DF"
    elif "MF" in pos:
        return "MF"
    elif "FW" in pos:
        return "FW"
    elif "GK" in pos:
        return "GK"
    else:
        return "Sub"
