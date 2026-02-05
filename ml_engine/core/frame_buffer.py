import time

class EmptyRoomTracker:
    def __init__(self):
        self.last_person_time = time.time()

    def update(self, person_present):
        if person_present:
            self.last_person_time = time.time()

    def is_empty_long_enough(self, threshold):
        return time.time() - self.last_person_time > threshold


