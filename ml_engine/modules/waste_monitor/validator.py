def reject_trash(box):

    x1,y1,x2,y2 = box
    w = x2 - x1
    h = y2 - y1
    area = w * h

    # noise
    if area < 300:
        return True

    # human-like tall shapes
    if h > 3 * w:
        return True

    # extremely flat reflections
    if w > 6 * h:
        return True

    return False