def evaluate_severity(broken_items):
    if not broken_items:
        return None

    count = len(broken_items)

    if count >= 3:
        return "high"
    elif count == 2:
        return "medium"
    else:
        return "low"