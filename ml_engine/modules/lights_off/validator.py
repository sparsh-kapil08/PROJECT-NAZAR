def validate_detection(result):
    if result is None:
        return False

    if result["status"] != "confirmed":
        return False

    if not (result["lights_on"] or result["fan_on"]):
        return False

    return True
