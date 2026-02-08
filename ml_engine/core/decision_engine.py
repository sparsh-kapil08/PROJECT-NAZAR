from ml_engine.core.config import EMPTY_TIME_THRESHOLD
from ml_engine.detectors.person_detector import detect_person
from ml_engine.detectors.light_detector import detect_artificial_light
from ml_engine.detectors.fan_motion_detector import detect_fan_motion
from ml_engine.core.frame_buffer import EmptyRoomTracker

tracker = EmptyRoomTracker()

def process_frame(frame):
    person_present = detect_person(frame)
    tracker.update(person_present)

    if not tracker.is_empty_long_enough(EMPTY_TIME_THRESHOLD):
        return None

    lights_on = detect_artificial_light(frame)
    fan_on = detect_fan_motion(frame)

    if lights_on or fan_on:
        return {
            "issue": "energy_waste",
            "lights_on": lights_on,
            "fan_on": fan_on,
            "status": "confirmed"
        }

    return None
